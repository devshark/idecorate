from django.contrib.auth.models import User
from django.conf import settings
from django.db import DatabaseError, transaction
from models import CustomerProfile, CustomerStyleBoard, StyleboardItems, StyleBoardCartItems, KeepImages
from cart.models import CartTemp, ProductPrice
import urllib2, urllib
from admin.models import TextFonts, Embellishments, EmbellishmentsType
import time
import re
from django.db.models import Q
from urllib import unquote
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
from plata.shop.models import Order, OrderItem

@transaction.commit_manually
def register_user(data):

    try:

        user = User.objects.create_user(data['username'], "", data['password'])
        user.email = data['username']
        user.first_name = data['firstname']
        user.last_name = data['lastname']
        user.is_active = True
        user.save()

        cp = CustomerProfile()
        cp.user = user
        cp.nickname = data['username']
        cp.save()
        transaction.commit()

        return user

    except Exception as e:

        transaction.rollback()
        
        return None

def is_registered(uname):
    return User.objects.filter(username=uname).exists() or User.objects.filter(email=uname).exists()

def customer_profile(user):
    profile = {}
    picture = None
    description = None
    try:
        customer = CustomerProfile.objects.get(user=user)
        nickname = customer.nickname
        username = customer.user.username
        first_name = customer.user.first_name
        last_name = customer.user.last_name
        email = customer.user.email
        picture = customer.picture
        description = customer.description
    except:
        nickname = user.username
        username = nickname
        first_name = user.first_name
        last_name = user.last_name
        email = user.email

    profile['nickname'] = nickname
    profile['username'] = username
    profile['first_name'] = first_name
    profile['last_name'] = last_name
    profile['email'] = email
    profile['picture'] = picture
    profile['description'] = description

    return profile

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_styleboard(user=None,styleboard_id=None):
    styleboards = None
    if user:
        styleboards = CustomerStyleBoard.objects.filter(user=user,styleboard_item__deleted=0)
    elif styleboard_id:
        try:
            styleboards = CustomerStyleBoard.objects.get(styleboard_item__id=styleboard_id, styleboard_item__deleted=0)
        except:
            styleboards = None

    return styleboards

def get_user_orders(user=None):

    if user:
        orders = Order.objects.filter(Q(user__id=user.id)).filter(Q(status__gt=20))
        return orders
    else :
        return False

def get_user_order(order_id,user=None):

    if user:

        try:
            data = {}
            order               = Order.objects.get(user__id=user.id,id=order_id)
            order_items         = OrderItem.objects.filter(order=order_id)
            data['order']       = order
            data['order_items'] = order_items
            return data

        except Exception as e:
            print e
            return False

    else :

        return False

def get_order(order_id):

    try:
        data = {}
        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order_id)
        data['order'] = order
        data['order_items'] = order_items

        return data
        
    except :

        pass

@transaction.commit_manually
def save_styleboard_item(data):
    try:
        customer_styleboard = data['customer_styleboard']
        mode = 'new'

        if customer_styleboard:

            st = customer_styleboard.styleboard_item
            csb = customer_styleboard
            mode = 'edit'

        else:

            st = StyleboardItems()
            csb = CustomerStyleBoard()

        st.name = data['name']
        st.description = data['description']
        st.item = data['item']
        st.browser = data['browser']
        st.item_guest = data['guest']
        st.item_tables = data['tables']
        st.save()

        csb.user = data['user']

        if 'personalize_total' in data:
            if data['personalize_total']:
                csb.total_price = data['personalize_total']
        
        if 'product_positions' in data['session_in_request']:
            p_position = data['session_in_request'].get('product_positions')
            if 'total' in p_position:
                csb.total_price = p_position.get('total','0.00')

        csb.styleboard_item = st
        csb.save()

        manage_styleboard_cart_items(data['sessionid'],st,mode)     
        transaction.commit()
        return csb
    except Exception as e:
        print "The error is: %s" % e    
        transaction.rollback()
        return False

def get_customer_styleboard_item(customer_styleboard):
    return CustomerStyleBoard.objects.get(id=customer_styleboard.id)

def manage_styleboard_cart_items(sessionid, styleboard_item, mode):
    # print "The mode is: %s" % mode
    cart_temp_items = CartTemp.objects.filter(sessionid=sessionid)
    
    # print "The cart_temp count is: %s" % cart_temp_items.count()
    if cart_temp_items.count()>0:
        for item in cart_temp_items:
            save_styleboard_cart_item(item.product, item.quantity, styleboard_item)
    """
    delete item in StyleBoardCartItems when it is deleted
    """
    if mode == 'edit':
        styleboard_cart = StyleBoardCartItems.objects.filter(styleboard_item=styleboard_item)
        for item_cart in styleboard_cart:
            is_exist = CartTemp.objects.filter(sessionid=sessionid, product=item_cart.product).count()
            if is_exist == 0:
                item_cart.delete()


def save_styleboard_cart_item(product, quantity, styleboard_item):  
    try:
        styleboard_cart = StyleBoardCartItems.objects.get(product=product, styleboard_item=styleboard_item)     
        if styleboard_cart.quantity != quantity:
            styleboard_cart.quantity = quantity
            styleboard_cart.save()
    except:
        styleboard_cart = StyleBoardCartItems()
        styleboard_cart.styleboard_item = styleboard_item
        styleboard_cart.product = product
        styleboard_cart.quantity = quantity
        styleboard_cart.save()

def get_save_styleboard_total(styleboard_item_id):
    items = StyleBoardCartItems.objects.filter(styleboard_item__id=styleboard_item_id)
    res = {}
    total_amount = 0
    for item in items:
        price = ProductPrice.objects.get(product=item.product)
        total_amount += (price._unit_price)*item.quantity

    return total_amount

def get_styleboard_cart_item(styleboard_item=None,styleboard_item_id=None):
    if styleboard_item:
        return StyleBoardCartItems.objects.filter(styleboard_item=styleboard_item).order_by('id')
    elif styleboard_item_id:
        return StyleBoardCartItems.objects.filter(styleboard_item__id=styleboard_item_id).order_by('id')
    return False

def get_facebook_friends(access_token, name, limit, offset):

    #"https://graph.facebook.com/%s/members?%s" % (d['id'], urllib.urlencode({'access_token': response['access_token']}))
    if name:
        fql = "SELECT name, uid FROM user WHERE uid IN(SELECT uid2 FROM friend WHERE uid1 = me()) AND strpos(lower(name),lower('%s')) >=0 ORDER BY name LIMIT %s,%s" % (name, offset, limit)
    else:
        fql = "SELECT name, uid FROM user WHERE uid IN(SELECT uid2 FROM friend WHERE uid1 = me()) ORDER BY name LIMIT %s,%s" % (offset, limit)

    fql_url = "https://graph.facebook.com/fql?%s" % urllib.urlencode({'q':fql, 'access_token': access_token})
    ret = {}
    try:
        connection = urllib2.urlopen(fql_url)
        responseString = connection.read()
        connection.close()

        print "The fql is: %s" % fql
        #print "The url is: %s" % fql_url
        #print "The responseString is: %s" % responseString

        exec("ret=%s" % responseString)
        return ret
    except Exception as e:
        print "Error fetching friends: %s" % e
        return ret

def get_user_keep_images(user=None):
    images = None
    
    if user:

        try:
            images = KeepImages.objects.filter(user=user).order_by('image__home_banner__size')
        except:
            images = None

    return images

def get_user_keep_image(image_id, user=None):
    image = None
    
    if user:

        try:
            image = KeepImages.objects.get(id=image_id, user=user)
        except:
            image = None

    return image

def save_styleboard_as_image(sbid):

    return dynamic_styleboard(sbid,500,317,True)#200

def dynamic_styleboard(id, w, h, isImage=False):

    styleboardItem = StyleboardItems.objects.get(id=id)
    itemString = str(styleboardItem.item).replace(',null','')
    itemList = []
    
    imageWidth = int(w)
    imageHeight = int(h)

    lowestTop = None
    highestTop = None
    lowestLeft = None
    highestLeft = None

    finalHeight = 0
    finalWidth = 0
    widthIndex = 0
    heightIndex = 0
    true = True
    false = False

    exec('itemList=%s' % itemString)

    for iList in itemList:

        try:
            if re.search('/media/products/',iList['img'][0]['src']):

                imgFile = iList['img'][0]['src'].split('/')
                imgFile = imgFile[len(imgFile) - 1].split('?')[0]
                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'products/', unquote(imgFile))

            elif re.search('/generate_embellishment/', iList['img'][0]['src']):
                eProperties = iList['img'][0]['src'].split("?")[1].split('&')

                directory = ""

                embObj = Embellishments.objects.get(id=int(eProperties[0].split('=')[1]))

                if embObj.e_type.id == 1:
                    directory = "images"
                elif embObj.e_type.id == 2:
                    directory = "textures"
                elif embObj.e_type.id == 3:
                    directory = "patterns"
                elif embObj.e_type.id == 4:
                    directory = "shapes"
                elif embObj.e_type.id == 5:
                    directory = "borders"

                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directory, embObj.image)
            elif re.search('/media/embellishments/',iList['img'][0]['src']):

                imgFile = iList['img'][0]['src'].split('/')
                imgFile = imgFile[len(imgFile) - 1]
                imgFile = imgFile.split('?')[0]
                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'embellishments/images/', unquote(imgFile))

            elif re.search('/generate_text/',iList['img'][0]['src']):
                eProperties = iList['img'][0]['src'].split("?")[1].split('&')

                fontObj = TextFonts.objects.get(id=int(eProperties[3].split('=')[1]))
                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "fonts/", fontObj.font)
                font_size = int(eProperties[0].split('=')[1])
                font_color = eProperties[2].split('=')[1]
                font_color = (int(font_color[0:3]), int(font_color[3:6]), int(font_color[6:9]))
                image_text = unquote(eProperties[1].split('=')[1])
            elif re.search('/cropped/',iList['img'][0]['src']):
                eProperties = iList['img'][0]['src'].split("?")[1].split('&')

                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "products/", unquote(eProperties[3].split('=')[1]))
                task = eProperties[1].split('=')[1]

                splittedPosts = unquote(eProperties[2].split('=')[1]).split(',')
        except KeyError:
            continue

        style = iList['style']
        splittedStyle = style.split(';')

        #find width and height index
        ctr = 0
        for item in splittedStyle:
            if re.search('width', item):
                widthIndex = ctr
            if re.search('height', item):
                heightIndex = ctr
            ctr += 1

        w = int(float(str(splittedStyle[widthIndex].split(':')[1]).strip().replace('px','')))
        h = int(float(str(splittedStyle[heightIndex].split(':')[1]).strip().replace('px','')))

        try:
            if re.search('/generate_text/',iList['img'][0]['src']):

                font = ImageFont.truetype(imgFile, font_size)
                
                image_text = image_text.replace("\r", "")
                splittedTexts = image_text.split("\n")
                totalHeight = 0
                upperWidth = 0
                heightList = [0]

                #compute the final width and height first
                for splittedText in splittedTexts:
                    textSize = font.getsize(splittedText)
                    totalHeight += textSize[1]
                    heightList.append(totalHeight)

                    if upperWidth == 0:
                        upperWidth = textSize[0]
                    else:
                        if textSize[0] > upperWidth:
                            upperWidth = textSize[0]

                #image with background transparent
                img = Image.new("RGBA", (upperWidth, totalHeight), (255,255,255, 0))
                #create draw object 
                draw = ImageDraw.Draw(img)
                #draw the text
                ctr = 0

                for splittedText in splittedTexts:
                    #draw text
                    draw.text((0,heightList[ctr]), splittedText, font_color, font=font)
                    ctr += 1

                imgObj = img
                #imgObj.thumbnail((w,h),Image.ANTIALIAS)
                imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
                imgObj = imgObj.rotate(float(iList['angle']), expand=1)
                w, h = imgObj.size
            elif re.search('/cropped/',iList['img'][0]['src']):

                img = Image.open(imgFile)
                back = Image.new('RGBA', (400,400), (255, 255, 255, 0))
                back.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))

                poly = Image.new('RGBA', (settings.PRODUCT_WIDTH,settings.PRODUCT_HEIGHT), (255, 255, 255, 0))
                pdraw = ImageDraw.Draw(poly)

                dimensionList = []

                if task == 'poly':
                    for splittedPost in splittedPosts:
                        spl = splittedPost.split(':')
                        dimensionList.append((float(spl[0]),float(spl[1])))

                    pdraw.polygon(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

                elif task == 'rect':
                    for splittedPost in splittedPosts:
                        dimensionList.append(float(splittedPost))
                    pdraw.rectangle(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))


                poly.paste(back,mask=poly)

                newImg = poly.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))
                imgObj = newImg
                imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
                imgObj = imgObj.rotate(float(iList['angle']), expand=1)
                w, h = imgObj.size
            else:
                imgObj = Image.open(imgFile).convert('RGBA')
                #imgObj.thumbnail((w,h),Image.ANTIALIAS)
                imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
                imgObj = imgObj.rotate(float(iList['angle']), expand=1)
                w, h = imgObj.size
        except:
            pass

        if lowestTop is None:
            lowestTop = int(float(iList['top']))
        else:
            if int(float(iList['top'])) < lowestTop:
                lowestTop = int(float(iList['top']))

        if highestTop is None:
            highestTop = int(float(iList['top'])) + h
        else:
            if (int(float(iList['top'])) + h) > highestTop:
                highestTop = int(float(iList['top'])) + h

        if lowestLeft is None:
            lowestLeft = int(float(iList['left']))
        else:
            if int(float(iList['left'])) < lowestLeft:
                lowestLeft = int(float(iList['left']))

        if highestLeft is None:
            highestLeft = int(float(iList['left'])) + w
        else:
            if (int(float(iList['left'])) + w) > highestLeft:
                highestLeft = int(float(iList['left'])) + w

    finalWidth = highestLeft - lowestLeft
    finalHeight = highestTop - lowestTop

    #create main image
    mainImage = Image.new('RGBA', (finalWidth, finalHeight), (255, 255, 255, 0))


    for iList in itemList:

        try:
            if re.search('/media/products/',iList['img'][0]['src']):

                imgFile = iList['img'][0]['src'].split('/')
                imgFile = imgFile[len(imgFile) - 1].split('?')[0]
                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'products/', unquote(imgFile))
            elif re.search('/generate_embellishment/', iList['img'][0]['src']):
                eProperties = iList['img'][0]['src'].split("?")[1].split('&')

                directory = ""

                embObj = Embellishments.objects.get(id=int(eProperties[0].split('=')[1]))

                if embObj.e_type.id == 1:
                    directory = "images"
                elif embObj.e_type.id == 2:
                    directory = "textures"
                elif embObj.e_type.id == 3:
                    directory = "patterns"
                elif embObj.e_type.id == 4:
                    directory = "shapes"
                elif embObj.e_type.id == 5:
                    directory = "borders"

                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directory, embObj.image)
            elif re.search('/media/embellishments/',iList['img'][0]['src']):

                imgFile = iList['img'][0]['src'].split('/')
                imgFile = imgFile[len(imgFile) - 1]
                imgFile = imgFile.split('?')[0]
                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'embellishments/images/', unquote(imgFile))

                """
                if re.search('?', imgFile):
                    splRnd = imgFile.split('?')
                    imgFile = splRnd[0]
                """
            elif re.search('/generate_text/',iList['img'][0]['src']):
                eProperties = iList['img'][0]['src'].split("?")[1].split('&')

                fontObj = TextFonts.objects.get(id=int(eProperties[3].split('=')[1]))
                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "fonts/", fontObj.font)
                font_size = int(eProperties[0].split('=')[1])
                font_color = eProperties[2].split('=')[1]
                font_color = (int(font_color[0:3]), int(font_color[3:6]), int(font_color[6:9]))
                image_text = unquote(eProperties[1].split('=')[1])
                #print "The text is: %s" % image_text
            elif re.search('/cropped/',iList['img'][0]['src']):
                eProperties = iList['img'][0]['src'].split("?")[1].split('&')

                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "products/", unquote(eProperties[3].split('=')[1]))
                task = eProperties[1].split('=')[1]

                splittedPosts = unquote(eProperties[2].split('=')[1]).split(',')
        except KeyError:
            continue

        style = iList['style']
        splittedStyle = style.split(';')

        #find width and height index
        ctr = 0
        for item in splittedStyle:
            if re.search('width', item):
                widthIndex = ctr
            if re.search('height', item):
                heightIndex = ctr
            ctr += 1

        w = int(float(str(splittedStyle[widthIndex].split(':')[1]).strip().replace('px','')))
        h = int(float(str(splittedStyle[heightIndex].split(':')[1]).strip().replace('px','')))


        if re.search('/generate_text/',iList['img'][0]['src']):

            font = ImageFont.truetype(imgFile, font_size)
            
            image_text = image_text.replace("\r", "")   
            splittedTexts = image_text.split("\n")
            totalHeight = 0
            upperWidth = 0
            heightList = [0]

            #compute the final width and height first
            for splittedText in splittedTexts:
                textSize = font.getsize(splittedText)
                totalHeight += textSize[1]
                heightList.append(totalHeight)

                if upperWidth == 0:
                    upperWidth = textSize[0]
                else:
                    if textSize[0] > upperWidth:
                        upperWidth = textSize[0]

            #image with background transparent
            img = Image.new("RGBA", (upperWidth, totalHeight), (255,255,255, 0))
            #create draw object 
            draw = ImageDraw.Draw(img)
            #draw the text
            ctr = 0

            for splittedText in splittedTexts:
                #draw text
                draw.text((0,heightList[ctr]), splittedText, font_color, font=font)
                ctr += 1

            imgObj = img
        elif re.search('/cropped/',iList['img'][0]['src']):

            img = Image.open(imgFile)
            back = Image.new('RGBA', (400,400), (255, 255, 255, 0))
            back.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))

            poly = Image.new('RGBA', (settings.PRODUCT_WIDTH,settings.PRODUCT_HEIGHT), (255, 255, 255, 0))
            pdraw = ImageDraw.Draw(poly)

            dimensionList = []

            if task == 'poly':
                for splittedPost in splittedPosts:
                    spl = splittedPost.split(':')
                    dimensionList.append((float(spl[0]),float(spl[1])))

                pdraw.polygon(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

            elif task == 'rect':
                for splittedPost in splittedPosts:
                    dimensionList.append(float(splittedPost))
                pdraw.rectangle(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

            poly.paste(back,mask=poly)

            newImg = poly.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))

            """
            splittedName = getExtensionAndFileName(imgFile)
            if splittedName[1] == '.jpg':
                img2 = Image.open("%s%s" % (settings.MEDIA_ROOT, "products/white_background.png"))
                img2 = img2.resize((newImg.size[0],newImg.size[1]), Image.ANTIALIAS)
                img2 = img2.convert('RGBA')             
                #img2 = Image.blend(img2, newImg, 0.0)
                img2.paste(newImg, mask=newImg)
                newImg = img2
            """
            imgObj = newImg
        else:
            #print "The type is: %s and it is else" % iList['_type']
            
            imgObj = Image.open(imgFile).convert('RGBA')

            if iList['_type'] == "box":
                boxImage = Image.new("RGBA", (w,h), (255,255,255,0))
                imgObj.thumbnail((w,h), Image.ANTIALIAS)
                boxImage.paste(imgObj, ((w - imgObj.size[0]) / 2, (h - imgObj.size[1]) /2 ))
                imgObj = boxImage

        if re.search('/generate_embellishment/', iList['img'][0]['src']):
            embellishment_color = eProperties[1].split('=')[1]
            embellishment_color = (int(embellishment_color[0:3]), int(embellishment_color[3:6]), int(embellishment_color[6:9]))
            newImg = Image.new("RGBA", imgObj.size, embellishment_color)
            r, g, b, alpha = imgObj.split()

            if embObj.e_type.id == 3:
                newImg.paste(imgObj, mask=b)
                imgObj = newImg
            elif embObj.e_type.id == 2 or embObj.e_type.id == 4:
                imgObj.paste(newImg, mask=alpha)


        #apply opacity
        if int(iList['opacity']) != 100:
            #adjust opacity
            floatOpacity = float(float(iList['opacity']) / float(100))
            alpha = imgObj.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(floatOpacity)
            imgObj.putalpha(alpha)

        #try to rotate
        try:
            #imgObj.thumbnail((w,h),Image.ANTIALIAS)
            imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
            imgObj = imgObj.rotate(float(iList['angle']), expand=1,resample=Image.BICUBIC)
            """
            print "The width is: %s, and height is: %s" % (w,h)
            print "The new width is: %s, and the new height is: %s" % imgObj.size
            
            aW = int((w / 2) * math.cos(float(iList['angle']))) + int((h / 2) * math.cos(90 - float(iList['angle'])))
            aH = int((w / 2) * math.sin(float(iList['angle']))) + int((h / 2) * math.sin(90 - float(iList['angle'])))
            
            
            imgObj.thumbnail((w,h),Image.ANTIALIAS)
            """
        except:
            #imgObj.thumbnail((w,h),Image.ANTIALIAS)
            imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
            

        #flip and flap
        exec('matrix=%s' % iList['matrix'])

        if matrix[0]['e']:
            #flip
            imgObj = imgObj.transpose(Image.FLIP_TOP_BOTTOM)

        if matrix[0]['f']:
            #flap
            imgObj = imgObj.transpose(Image.FLIP_LEFT_RIGHT)
        
        """
        try:

            if splittedName[1] == '.jpg':
                mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop))
            else:   
                mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop), mask=imgObj)
        except:

            mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop), mask=imgObj)
        """
        mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop), mask=imgObj)
        #paste image
        #mainImage.paste(imgObj, (highestWidth - (w + int(iList['left'])), highestHeight - (h + int(iList['top']))))
    
    mainImage.thumbnail((imageWidth,imageHeight), Image.ANTIALIAS)
    bgImg = Image.new('RGBA', (imageWidth, imageHeight), (255, 255, 255, 0))
    bgImg.paste(mainImage,((imageWidth - mainImage.size[0]) / 2, (imageHeight - mainImage.size[1]) / 2))
    
    if isImage:
        time_name       = time.time()
        time_name       = str(time_name)
        file_name_temp  = time_name.replace('.','_')
        file_name       = 'sb_%s_%s.%s' % (id,file_name_temp,'png')

        path = '%sstyleboards/%s' % (settings.MEDIA_ROOT,file_name)

        bgImg.save(path, "PNG")

        return file_name
        
    else:
        
        return bgImg

def print_styleboard(data, w, h, isImage=False):

    itemString = str(data).replace(',null','')
    itemList = []
    
    imageWidth = int(w)
    imageHeight = int(h)

    lowestTop = None
    highestTop = None
    lowestLeft = None
    highestLeft = None

    finalHeight = 0
    finalWidth = 0
    widthIndex = 0
    heightIndex = 0
    true = True
    false = False
    
    exec('itemList=%s' % itemString)

    for iList in itemList:

        try:
            if re.search('/media/products/',iList['img'][0]['src']):

                imgFile = iList['img'][0]['src'].split('/')
                imgFile = imgFile[len(imgFile) - 1].split('?')[0]
                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'products/', unquote(imgFile))

            elif re.search('/generate_embellishment/', iList['img'][0]['src']):
                eProperties = iList['img'][0]['src'].split("?")[1].split('&')

                directory = ""

                embObj = Embellishments.objects.get(id=int(eProperties[0].split('=')[1]))

                if embObj.e_type.id == 1:
                    directory = "images"
                elif embObj.e_type.id == 2:
                    directory = "textures"
                elif embObj.e_type.id == 3:
                    directory = "patterns"
                elif embObj.e_type.id == 4:
                    directory = "shapes"
                elif embObj.e_type.id == 5:
                    directory = "borders"

                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directory, embObj.image)
            elif re.search('/media/embellishments/',iList['img'][0]['src']):

                imgFile = iList['img'][0]['src'].split('/')
                imgFile = imgFile[len(imgFile) - 1]
                imgFile = imgFile.split('?')[0]
                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'embellishments/images/', unquote(imgFile))

            elif re.search('/generate_text/',iList['img'][0]['src']):
                eProperties = iList['img'][0]['src'].split("?")[1].split('&')

                fontObj = TextFonts.objects.get(id=int(eProperties[3].split('=')[1]))
                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "fonts/", fontObj.font)
                font_size = int(eProperties[0].split('=')[1])
                font_color = eProperties[2].split('=')[1]
                font_color = (int(font_color[0:3]), int(font_color[3:6]), int(font_color[6:9]))
                image_text = unquote(eProperties[1].split('=')[1])
            elif re.search('/cropped/',iList['img'][0]['src']):
                eProperties = iList['img'][0]['src'].split("?")[1].split('&')

                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "products/", unquote(eProperties[3].split('=')[1]))
                task = eProperties[1].split('=')[1]

                splittedPosts = unquote(eProperties[2].split('=')[1]).split(',')
        except KeyError:
            continue

        style = iList['style']
        splittedStyle = style.split(';')

        #find width and height index
        ctr = 0
        for item in splittedStyle:
            if re.search('width', item):
                widthIndex = ctr
            if re.search('height', item):
                heightIndex = ctr
            ctr += 1

        w = int(float(str(splittedStyle[widthIndex].split(':')[1]).strip().replace('px','')))
        h = int(float(str(splittedStyle[heightIndex].split(':')[1]).strip().replace('px','')))

        try:
            if re.search('/generate_text/',iList['img'][0]['src']):

                font = ImageFont.truetype(imgFile, font_size)
                
                image_text = image_text.replace("\r", "")
                splittedTexts = image_text.split("\n")
                totalHeight = 0
                upperWidth = 0
                heightList = [0]

                #compute the final width and height first
                for splittedText in splittedTexts:
                    textSize = font.getsize(splittedText)
                    totalHeight += textSize[1]
                    heightList.append(totalHeight)

                    if upperWidth == 0:
                        upperWidth = textSize[0]
                    else:
                        if textSize[0] > upperWidth:
                            upperWidth = textSize[0]

                #image with background transparent
                img = Image.new("RGBA", (upperWidth, totalHeight), (255,255,255, 0))
                #create draw object 
                draw = ImageDraw.Draw(img)
                #draw the text
                ctr = 0

                for splittedText in splittedTexts:
                    #draw text
                    draw.text((0,heightList[ctr]), splittedText, font_color, font=font)
                    ctr += 1

                imgObj = img
                #imgObj.thumbnail((w,h),Image.ANTIALIAS)
                imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
                imgObj = imgObj.rotate(float(iList['angle']), expand=1)
                w, h = imgObj.size
            elif re.search('/cropped/',iList['img'][0]['src']):

                img = Image.open(imgFile)
                back = Image.new('RGBA', (400,400), (255, 255, 255, 0))
                back.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))

                poly = Image.new('RGBA', (settings.PRODUCT_WIDTH,settings.PRODUCT_HEIGHT), (255, 255, 255, 0))
                pdraw = ImageDraw.Draw(poly)

                dimensionList = []

                if task == 'poly':
                    for splittedPost in splittedPosts:
                        spl = splittedPost.split(':')
                        dimensionList.append((float(spl[0]),float(spl[1])))

                    pdraw.polygon(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

                elif task == 'rect':
                    for splittedPost in splittedPosts:
                        dimensionList.append(float(splittedPost))
                    pdraw.rectangle(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))


                poly.paste(back,mask=poly)

                newImg = poly.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))
                imgObj = newImg
                imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
                imgObj = imgObj.rotate(float(iList['angle']), expand=1)
                w, h = imgObj.size
            else:
                imgObj = Image.open(imgFile).convert('RGBA')
                #imgObj.thumbnail((w,h),Image.ANTIALIAS)
                imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
                imgObj = imgObj.rotate(float(iList['angle']), expand=1)
                w, h = imgObj.size
        except:
            pass

        if lowestTop is None:
            lowestTop = int(float(iList['top']))
        else:
            if int(float(iList['top'])) < lowestTop:
                lowestTop = int(float(iList['top']))

        if highestTop is None:
            highestTop = int(float(iList['top'])) + h
        else:
            if (int(float(iList['top'])) + h) > highestTop:
                highestTop = int(float(iList['top'])) + h

        if lowestLeft is None:
            lowestLeft = int(float(iList['left']))
        else:
            if int(float(iList['left'])) < lowestLeft:
                lowestLeft = int(float(iList['left']))

        if highestLeft is None:
            highestLeft = int(float(iList['left'])) + w
        else:
            if (int(float(iList['left'])) + w) > highestLeft:
                highestLeft = int(float(iList['left'])) + w

    finalWidth = highestLeft - lowestLeft
    finalHeight = highestTop - lowestTop

    #create main image
    mainImage = Image.new('RGBA', (finalWidth, finalHeight), (255, 255, 255, 0))


    for iList in itemList:

        try:
            if re.search('/media/products/',iList['img'][0]['src']):

                imgFile = iList['img'][0]['src'].split('/')
                imgFile = imgFile[len(imgFile) - 1].split('?')[0]
                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'products/', unquote(imgFile))
            elif re.search('/generate_embellishment/', iList['img'][0]['src']):
                eProperties = iList['img'][0]['src'].split("?")[1].split('&')

                directory = ""

                embObj = Embellishments.objects.get(id=int(eProperties[0].split('=')[1]))

                if embObj.e_type.id == 1:
                    directory = "images"
                elif embObj.e_type.id == 2:
                    directory = "textures"
                elif embObj.e_type.id == 3:
                    directory = "patterns"
                elif embObj.e_type.id == 4:
                    directory = "shapes"
                elif embObj.e_type.id == 5:
                    directory = "borders"

                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directory, embObj.image)
            elif re.search('/media/embellishments/',iList['img'][0]['src']):

                imgFile = iList['img'][0]['src'].split('/')
                imgFile = imgFile[len(imgFile) - 1]
                imgFile = imgFile.split('?')[0]
                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'embellishments/images/', unquote(imgFile))

                """
                if re.search('?', imgFile):
                    splRnd = imgFile.split('?')
                    imgFile = splRnd[0]
                """
            elif re.search('/generate_text/',iList['img'][0]['src']):
                eProperties = iList['img'][0]['src'].split("?")[1].split('&')

                fontObj = TextFonts.objects.get(id=int(eProperties[3].split('=')[1]))
                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "fonts/", fontObj.font)
                font_size = int(eProperties[0].split('=')[1])
                font_color = eProperties[2].split('=')[1]
                font_color = (int(font_color[0:3]), int(font_color[3:6]), int(font_color[6:9]))
                image_text = unquote(eProperties[1].split('=')[1])
                #print "The text is: %s" % image_text
            elif re.search('/cropped/',iList['img'][0]['src']):
                eProperties = iList['img'][0]['src'].split("?")[1].split('&')

                imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "products/", unquote(eProperties[3].split('=')[1]))
                task = eProperties[1].split('=')[1]

                splittedPosts = unquote(eProperties[2].split('=')[1]).split(',')
        except KeyError:
            continue

        style = iList['style']
        splittedStyle = style.split(';')

        #find width and height index
        ctr = 0
        for item in splittedStyle:
            if re.search('width', item):
                widthIndex = ctr
            if re.search('height', item):
                heightIndex = ctr
            ctr += 1

        w = int(float(str(splittedStyle[widthIndex].split(':')[1]).strip().replace('px','')))
        h = int(float(str(splittedStyle[heightIndex].split(':')[1]).strip().replace('px','')))


        if re.search('/generate_text/',iList['img'][0]['src']):

            font = ImageFont.truetype(imgFile, font_size)
            
            image_text = image_text.replace("\r", "")   
            splittedTexts = image_text.split("\n")
            totalHeight = 0
            upperWidth = 0
            heightList = [0]

            #compute the final width and height first
            for splittedText in splittedTexts:
                textSize = font.getsize(splittedText)
                totalHeight += textSize[1]
                heightList.append(totalHeight)

                if upperWidth == 0:
                    upperWidth = textSize[0]
                else:
                    if textSize[0] > upperWidth:
                        upperWidth = textSize[0]

            #image with background transparent
            img = Image.new("RGBA", (upperWidth, totalHeight), (255,255,255, 0))
            #create draw object 
            draw = ImageDraw.Draw(img)
            #draw the text
            ctr = 0

            for splittedText in splittedTexts:
                #draw text
                draw.text((0,heightList[ctr]), splittedText, font_color, font=font)
                ctr += 1

            imgObj = img
        elif re.search('/cropped/',iList['img'][0]['src']):

            img = Image.open(imgFile)
            back = Image.new('RGBA', (400,400), (255, 255, 255, 0))
            back.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))

            poly = Image.new('RGBA', (settings.PRODUCT_WIDTH,settings.PRODUCT_HEIGHT), (255, 255, 255, 0))
            pdraw = ImageDraw.Draw(poly)

            dimensionList = []

            if task == 'poly':
                for splittedPost in splittedPosts:
                    spl = splittedPost.split(':')
                    dimensionList.append((float(spl[0]),float(spl[1])))

                pdraw.polygon(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

            elif task == 'rect':
                for splittedPost in splittedPosts:
                    dimensionList.append(float(splittedPost))
                pdraw.rectangle(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

            poly.paste(back,mask=poly)

            newImg = poly.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))

            imgObj = newImg
        else:
            #print "The type is: %s and it is else" % iList['_type']
            
            imgObj = Image.open(imgFile).convert('RGBA')

            if iList['_type'] == "box":
                boxImage = Image.new("RGBA", (w,h), (255,255,255,0))
                imgObj.thumbnail((w,h), Image.ANTIALIAS)
                boxImage.paste(imgObj, ((w - imgObj.size[0]) / 2, (h - imgObj.size[1]) /2 ))
                imgObj = boxImage

        if re.search('/generate_embellishment/', iList['img'][0]['src']):
            embellishment_color = eProperties[1].split('=')[1]
            embellishment_color = (int(embellishment_color[0:3]), int(embellishment_color[3:6]), int(embellishment_color[6:9]))
            newImg = Image.new("RGBA", imgObj.size, embellishment_color)
            r, g, b, alpha = imgObj.split()

            if embObj.e_type.id == 3:
                newImg.paste(imgObj, mask=b)
                imgObj = newImg
            elif embObj.e_type.id == 2 or embObj.e_type.id == 4:
                imgObj.paste(newImg, mask=alpha)


        #apply opacity
        if int(iList['opacity']) != 100:
            #adjust opacity
            floatOpacity = float(float(iList['opacity']) / float(100))
            alpha = imgObj.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(floatOpacity)
            imgObj.putalpha(alpha)

        #try to rotate
        try:
            #imgObj.thumbnail((w,h),Image.ANTIALIAS)
            imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
            imgObj = imgObj.rotate(float(iList['angle']), expand=1,resample=Image.BICUBIC)
            
        except:
            #imgObj.thumbnail((w,h),Image.ANTIALIAS)
            imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
            

        #flip and flap
        exec('matrix=%s' % iList['matrix'])

        if matrix[0]['e']:
            #flip
            imgObj = imgObj.transpose(Image.FLIP_TOP_BOTTOM)

        if matrix[0]['f']:
            #flap
            imgObj = imgObj.transpose(Image.FLIP_LEFT_RIGHT)
        
       
        mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop), mask=imgObj)
        #paste image
        #mainImage.paste(imgObj, (highestWidth - (w + int(iList['left'])), highestHeight - (h + int(iList['top']))))
    
    mainImage.thumbnail((imageWidth,imageHeight), Image.ANTIALIAS)
    bgImg = Image.new('RGBA', (imageWidth, imageHeight), (255, 255, 255, 0))
    bgImg.paste(mainImage,((imageWidth - mainImage.size[0]) / 2, (imageHeight - mainImage.size[1]) / 2))
    
    if isImage:
        
        time_name       = time.time()
        time_name       = str(time_name)
        file_name_temp  = time_name.replace('.','_')
        file_name       = 'print_sb_%s.%s' % (file_name_temp,'png')

        path = '%sstyleboards/%s' % (settings.MEDIA_ROOT,file_name)

        bgImg.save(path, "PNG")

        return file_name
        
    else:
        
        return bgImg