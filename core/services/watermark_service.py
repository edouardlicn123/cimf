"""
================================================================================
文件：watermark_service.py
路径：/home/edo/cimf-v2/core/services/watermark_service.py
================================================================================

功能说明：
    水印服务，提供服务端图片水印功能

    主要功能：
    - 添加文字水印
    - 添加图片水印
    - 支持位置和透明度配置

用法：
    1. 添加文字水印：
        WatermarkService.add_text_watermark(image_path, output_path, 'Hello')

    2. 添加图片水印：
        WatermarkService.add_image_watermark(image_path, output_path, logo_path)

版本：
    - 1.0: 初始版本

依赖：
    - PIL: 图片处理库
"""

import logging

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class WatermarkService:
    """
    水印服务类

    提供服务端水印功能，用于导出文件时添加水印
    """

    POSITIONS = {
        "topleft": (10, 10, "lt"),
        "topright": (10, 10, "rt"),
        "bottomleft": (10, 10, "lb"),
        "bottomright": (10, 10, "rb"),
        "center": (0, 0, "cc"),
    }

    @classmethod
    def _get_position_coords(cls, position, img_width, img_height, marker_width, marker_height):
        config = cls.POSITIONS.get(position) or cls.POSITIONS.get(
            {
                "top_left": "topleft",
                "top_right": "topright",
                "bottom_left": "bottomleft",
                "bottom_right": "bottomright",
            }.get(position),
            cls.POSITIONS["center"],
        )
        margin_x, margin_y, anchor = config
        if anchor == "lt":
            return (margin_x, margin_y)
        elif anchor == "rt":
            return (img_width - marker_width - margin_x, margin_y)
        elif anchor == "lb":
            return (margin_x, img_height - marker_height - margin_y)
        elif anchor == "rb":
            return (img_width - marker_width - margin_x, img_height - marker_height - margin_y)
        elif anchor == "cc":
            return ((img_width - marker_width) // 2, (img_height - marker_height) // 2)
        return (margin_x, margin_y)

    @classmethod
    def add_text_watermark(
        cls,
        image_path: str,
        output_path: str,
        text: str,
        position: str = "center",
        opacity: float = 0.3,
        font_size: int = 48,
        color: tuple[int, int, int] = (128, 128, 128),
    ) -> bool:
        """
        添加文字水印

        参数：
            image_path: 原图路径
            output_path: 输出路径
            text: 水印文字
            position: 位置 (center, bottom_right, bottom_left, top_right, top_left)
            opacity: 透明度 0-1
            font_size: 字体大小
            color: RGB 颜色

        返回：
            是否成功
        """
        try:
            img = Image.open(image_path).convert("RGBA")

            watermark = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(watermark)

            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except Exception:  # noqa: CIMF_W007 — font file not available, use default
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            img_width, img_height = img.size

            pos = cls._get_position_coords(position, img_width, img_height, text_width, text_height)

            alpha = int(255 * opacity)
            draw.text(pos, text, font=font, fill=(*color, alpha))

            watermarked = Image.alpha_composite(img, watermark)

            if watermarked.mode == "RGBA":
                watermarked = watermarked.convert("RGB")

            watermarked.save(output_path)  # noqa: CIMF_W006 — PIL Image.save()
            return True

        except Exception as e:
            logger.error(f"添加水印失败: {e}", exc_info=True)
            return False

    @classmethod
    def add_image_watermark(
        cls,
        image_path: str,
        output_path: str,
        logo_path: str,
        position: str = "center",
        opacity: float = 0.5,
        size: tuple[int, int] | None = None,
    ) -> bool:
        """
        添加图片水印

        参数：
            image_path: 原图路径
            output_path: 输出路径
            logo_path: logo 图片路径
            position: 位置
            opacity: 透明度 0-1
            size: logo 尺寸 (width, height)

        返回：
            是否成功
        """
        try:
            img = Image.open(image_path).convert("RGBA")
            logo = Image.open(logo_path).convert("RGBA")

            if size:
                logo = logo.resize(size, Image.Resampling.LANCZOS)

            if logo.mode != "RGBA":
                logo = logo.convert("RGBA")

            alpha = logo.split()[3]
            alpha = alpha.point(lambda p: int(p * opacity))
            logo.putalpha(alpha)

            img_width, img_height = img.size
            logo_width, logo_height = logo.size

            pos = cls._get_position_coords(position, img_width, img_height, logo_width, logo_height)

            result = Image.new("RGBA", img.size, (255, 255, 255, 0))
            result.paste(img, (0, 0))
            result.paste(logo, pos, logo)

            if result.mode == "RGBA":
                result = result.convert("RGB")

            result.save(output_path)  # noqa: CIMF_W006 — PIL Image.save()
            return True

        except Exception as e:
            logger.error(f"添加图片水印失败: {e}", exc_info=True)
            return False
