"""
中古擬音韻分解工具，可將韻（IPA 形式）分解爲韻頭、韻腹、韻尾
----------
使用方法：
    from triungkoxim_yonh_decompose import decompose_yonh, YonhParts
    decomposed = decompose_yonh("ɯiɛm")
    for yonh_part in YonhParts:
        print("{}：{}".format(yonh_part.value, decomposed[yonh_part]))

期待輸出：
    韻頭：ɯi
    韻腹：ɛ
    韻尾：m
"""
import logging
import re
import unittest

from enum import Enum

MSG_INVALID_YONH = "韻「{}」格式不合法，請檢查。"

YONH_DU_IPAS = [
    "ʷɯi",
    "ʷi", "ʷɨ", "ʷɯ", "ɯi", # Combinations have the HIGHST priority
    "i", "j", "u", "w",
    "ɨ", "ɻ", "ʵ",
    "ɯ", "ɣ", "r",
    "ʷ", # Cominationable have the LOWEST Priority
]

YONH_PIUK_IPAS = [
    "i", "ɨ", "ɪ", "ɯ", "u",
    "e", "ɘ", "ə", "o", "ɤ",
    "ɛ", "ɐ", "ʌ", "ɔ", "ɑ",
    "æ", "a",
]

YONH_MYOIX_IPAS = [
    "u", "w", "i", "j", # 陰聲韻 -i, -u
    "m", "n", "ŋ", "ng", "ŋʷ", # 陽聲韻 -m -n -ng
    "p", "t", "k", "kʷ", # 入聲韻 -p -t -k
]

def to_re_groups(txt: list):
    return "(" + "|".join(txt) + ")"

class YonhParts(Enum):
    """
    分解類型枚舉
    ----------
    YONH_DU       韻頭
    YONH_PIUK     韻腹
    YONH_MYOIX    韻尾
    """
    YONH_DU    = "韻頭"
    YONH_PIUK  = "韻腹"
    YONH_MYOIX = "韻尾"

MATCHING_GROUP_INDECIES = {
    YonhParts.YONH_DU:    1,
    YonhParts.YONH_PIUK:  2,
    YonhParts.YONH_MYOIX: 3,
}

def decompose_yonh(yonh: str):
    # init
    pattern = get_pattern()
    logging.info("正在使用的表達式: %s", pattern)

    result = {}
    # matching
    matched = pattern.match(yonh)

    if matched:
        for yonh_part in YonhParts:
            result[yonh_part] = group if (group := matched.group(MATCHING_GROUP_INDECIES[yonh_part])) else ""
        if "".join(result.values()) != yonh:
            raise ValueError(MSG_INVALID_YONH.format(yonh))
    else:
        raise ValueError(MSG_INVALID_YONH.format(yonh))

    return result

# TODO: Cache
def get_pattern():
    YONH_DU = to_re_groups(YONH_DU_IPAS)
    YONH_PIUK = to_re_groups(YONH_PIUK_IPAS)
    YONH_MYOIX = to_re_groups(YONH_MYOIX_IPAS)
    return re.compile(r"{}{{0,1}}{}{{1}}{}{{0,1}}".format(YONH_DU, YONH_PIUK, YONH_MYOIX))

class Test(unittest.TestCase):
    TEST_STRINGS = {
        "ɑ": {
            YonhParts.YONH_DU:    "",
            YonhParts.YONH_PIUK:  "ɑ",
            YonhParts.YONH_MYOIX: "",
        },
        "uŋ": {
            YonhParts.YONH_DU:    "",
            YonhParts.YONH_PIUK:  "u",
            YonhParts.YONH_MYOIX: "ŋ",
        },
        "ui": {
            YonhParts.YONH_DU:    "u",
            YonhParts.YONH_PIUK:  "i",
            YonhParts.YONH_MYOIX: "",
        },
        "ʷɯa": {
            YonhParts.YONH_DU:    "ʷɯ",
            YonhParts.YONH_PIUK:  "a",
            YonhParts.YONH_MYOIX: "",
        },
        "iɐp": {
            YonhParts.YONH_DU:    "i",
            YonhParts.YONH_PIUK:  "ɐ",
            YonhParts.YONH_MYOIX: "p",
        },
    }

    def test_normal_case(self):
        for test_string, test_result in self.TEST_STRINGS.items():
            decomposed = decompose_yonh(test_string)
            self.assertEqual(decomposed, test_result)

    def test_exception(self):
        for test_string in ["", "abc", "cde"]:
            with self.assertRaises(ValueError):
                decompose_yonh(test_string)

if __name__ == "__main__":
    print("Testing...")
    unittest.main()
