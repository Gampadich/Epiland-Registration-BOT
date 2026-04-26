import re

def validateNumber(phone):
    'Validating phone number here and returning it in 0XXXXXXXXX from'

    digits = re.sub(r'\D', '', phone)

    if len(digits) == 10 and digits.startswith('0'):
        digits = '38' + digits
    elif len(digits) == 11 and digits.startswith('80'):
        digits = '3' + digits

    if len(digits) != 12 or not digits.startswith('380'):
        return False, "Неправильний формат. Використовуйте 0XXXXXXXXX."

    validCodes = {
        '39', '50', '63', '66', '67', '68', '73', '89', '91', '92', '93', '94', '95', '96', '97', '98', '99'
    }

    operatorCode = digits[3:5]

    if operatorCode in validCodes:
        localFormat = digits[2:]
        return True, localFormat
    else:
        return False, f"Код оператора ({operatorCode}) не існує в Україні."

