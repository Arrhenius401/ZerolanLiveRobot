from PIL.Image import Image

# 检查图像是否为单一颜色（均匀图像）
def is_image_uniform(img: Image):
    gray_img = img.convert('L')
    min_value, max_value = gray_img.getextrema()
    return min_value == max_value
