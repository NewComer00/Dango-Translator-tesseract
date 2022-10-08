import re
import pytesseract
from PIL import Image
from traceback import format_exc


# 图片四周加白边
def imageBorder(src, dst, loc="a", width=3, color=(0, 0, 0)):

    # 读取图片
    img_ori = Image.open(src)
    w = img_ori.size[0]
    h = img_ori.size[1]
    img_new = None

    # 添加边框
    if loc in ["a", "all"]:
        w += 2*width
        h += 2*width
        img_new = Image.new("RGB", (w, h), color)
        img_new.paste(img_ori, (width, width))
    elif loc in ["t", "top"]:
        h += width
        img_new = Image.new("RGB", (w, h), color)
        img_new.paste(img_ori, (0, width, w, h))
    elif loc in ["r", "right"]:
        w += width
        img_new = Image.new("RGB", (w, h), color)
        img_new.paste(img_ori, (0, 0, w-width, h))
    elif loc in ["b", "bottom"]:
        h += width
        img_new = Image.new("RGB", (w, h), color)
        img_new.paste(img_ori, (0, 0, w, h-width))
    elif loc in ["l", "left"]:
        w += width
        img_new = Image.new("RGB", (w, h), color)
        img_new.paste(img_ori, (width, 0, w, h))

    # 保存图片
    img_new.save(dst)

def tesseractOCR(config, logger, test=False) :
    language = config["tesseractLang"]
    exec_path = config["tesseractPath"]

    if not test :
        image_path = "./config/image.jpg"
    else :
        image_path = "./config/other/image_rus.jpg"

    try:
        # 给待识别图片的四周加上白边
        imageBorder(image_path, image_path, "a", 10, color=(255, 255, 255))

        # 指定tesseract可执行文件位置
        pytesseract.pytesseract.tesseract_cmd = exec_path

        # 根据图片识别文字
        result = pytesseract.image_to_string(image_path, lang=language)

        # 如果正常配置下没有识别到文字，使用更精细的配置再次识别
        # https://stackoverflow.com/a/44632770
        if result == "":
            result = pytesseract.image_to_string(image_path, lang=language, config='--psm 12')
            # 更精细的识别可能会把花纹误识别成特殊符号，若结果出现特殊符号，舍弃这个结果
            special_characters = r"@#$%^&*|'()[]{}-+_=<>/0"
            result = '' if any(c in special_characters for c in result) else result

        # 去掉白边
        image = Image.open(image_path)
        coordinate = (10, 10, image.width - 10, image.height - 10)
        region = image.crop(coordinate)
        region.save(image_path)

    except Exception as err :
        logger.error(format_exc())
        return False, "Tesseract OCR 出错: " + str(err)

    # 处理OCR结果的换行问题
    asian_lang_list = \
            ["chi_sim", "chi_tra", "jpn", "kor"] # 不以空格分词的一些语言
    # 如果要拼接OCR结果中由换行分隔开的句子，亚洲文字直接拼合，其他文字由空格符拼合
    if not config["BranchLineUse"] :
        if language in asian_lang_list :
            result = result.replace('\n', '')
        else :
            result = result.replace('\n', ' ')

    return True, result
