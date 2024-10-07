# Create your tests here.

import base64
import uuid


def main():
    # 假设 base64_string 是你的 base64 编码的字符串
    base64_string = "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"

    image_data = base64.b64decode(base64_string)
    image_filename = f"{uuid.uuid4()}.jpg"
    image_path = image_filename

    # 保存解码后的图片到服务器
    with open(image_path, 'wb') as image_file:
        image_file.write(image_data)

    print("图片已成功保存为 output_image.png")


if __name__ == "__main__":
    main()
