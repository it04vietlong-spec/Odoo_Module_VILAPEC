from odoo import models

class MoneyToText(models.AbstractModel):
    _name = "report.money_to_text_vi"
    _description = "Convert money amount to Vietnamese text"

    @staticmethod
    def number_to_text_vn(amount, currency="VND"):
        digits = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
        units = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ", "triệu tỷ"]

        currency_names = {
            "VND": ("đồng", "xu"),
            "USD": ("đô la Mỹ", "cent"),
            "EUR": ("euro", "cent"),
            "JPY": ("yên Nhật", ""),  # JPY không có tiền lẻ
            "CNY": ("nhân dân tệ", "xu"),
        }

        def read_three_digits(n, show_zero_hundred=False):
            result = ""
            hundreds = n // 100
            tens = (n % 100) // 10
            ones = n % 10

            if hundreds > 0:
                result += digits[hundreds] + " trăm"
            elif show_zero_hundred:
                result += "không trăm"

            if tens > 1:
                result += " " + digits[tens] + " mươi"
                if ones == 1:
                    result += " mốt"
                elif ones == 5:
                    result += " lăm"
                elif ones != 0:
                    result += " " + digits[ones]
            elif tens == 1:
                result += " mười"
                if ones == 1:
                    result += " một"
                elif ones == 5:
                    result += " lăm"
                elif ones != 0:
                    result += " " + digits[ones]
            elif tens == 0 and ones != 0:
                if hundreds != 0:
                    result += " lẻ " + digits[ones]
                else:
                    result += digits[ones]

            return result.strip()

        def convert_number(n):
            if n == 0:
                return "không"

            parts = []
            scale = 0
            groups = []

            while n > 0:
                groups.append((n % 1000, scale))
                n //= 1000
                scale += 1

            groups.reverse()
            group_count = len(groups)

            for idx, (group, scale) in enumerate(groups):
                is_first = (idx == 0)
                show_zero = not is_first
                if group != 0:
                    text = read_three_digits(group, show_zero)
                    if units[scale]:
                        text += " " + units[scale]
                    parts.append(text)

            return " ".join(parts).strip().replace("  ", " ")

        # Tách phần nguyên và phần lẻ
        integer_part = int(amount)
        decimal_part = round((amount - integer_part) * 100)

        major_unit, minor_unit = currency_names.get(currency, ("đơn vị", "phụ"))

        result_parts = []

        if integer_part == 0:
            result_parts.append("Không " + major_unit)
        else:
            int_text = convert_number(integer_part)
            result_parts.append(int_text[0].upper() + int_text[1:] + f" {major_unit}")

        if decimal_part > 0 and minor_unit:
            decimal_text = convert_number(decimal_part)
            result_parts.append("và " + decimal_text + f" {minor_unit}")

        return " ".join(result_parts)
