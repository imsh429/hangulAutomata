CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ',
                'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ',
                'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ',
                 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ',
                 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']

JONGSUNG_LIST = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ',
                 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ',
                 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ',
                 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

COMPOSED_JUNG = {
    ('ㅗ', 'ㅏ'): 'ㅘ',
    ('ㅗ', 'ㅐ'): 'ㅙ',
    ('ㅗ', 'ㅣ'): 'ㅚ',
    ('ㅜ', 'ㅓ'): 'ㅝ',
    ('ㅜ', 'ㅔ'): 'ㅞ',
    ('ㅜ', 'ㅣ'): 'ㅟ',
    ('ㅡ', 'ㅣ'): 'ㅢ',
    ('ㅏ', 'ㅣ'): 'ㅐ',
    ('ㅓ', 'ㅣ'): 'ㅔ',
}

COMPOSED_JONG = {
    ('ㄱ', 'ㅅ'): 'ㄳ',
    ('ㄴ', 'ㅈ'): 'ㄵ',
    ('ㄴ', 'ㅎ'): 'ㄶ',
    ('ㄹ', 'ㄱ'): 'ㄺ',
    ('ㄹ', 'ㅁ'): 'ㄻ',
    ('ㄹ', 'ㅂ'): 'ㄼ',
    ('ㄹ', 'ㅅ'): 'ㄽ',
    ('ㄹ', 'ㅌ'): 'ㄾ',
    ('ㄹ', 'ㅍ'): 'ㄿ',
    ('ㄹ', 'ㅎ'): 'ㅀ',
    ('ㅂ', 'ㅅ'): 'ㅄ',
}

def combine_hangul(cho, jung, jong=''):
    cho_index = CHOSUNG_LIST.index(cho)
    jung_index = JUNGSUNG_LIST.index(jung)
    jong_index = JONGSUNG_LIST.index(jong)
    return chr(0xAC00 + (cho_index * 21 * 28) + (jung_index * 28) + jong_index)

def determine(ch):
    if ch in CHOSUNG_LIST or ch in JONGSUNG_LIST:
        return 'jaeum'
    elif ch in JUNGSUNG_LIST:
        return 'moeum'
    else:
        return 'etc'

def make_hangul(line):
    cho, jung, jong = None, None, None
    result = []
    i = 0
    while i < len(line):
        ch = line[i]

        # 백스페이스 처리
        if ch == '<':
            if jong:
                jong = None
            elif jung:
                jung = None
            elif cho:
                cho = None
            elif result:
                result.pop()
            i += 1
            continue

        ch_type = determine(ch)
        
        # 자음 처리
        if ch_type == 'jaeum':
            if cho is None:
                cho = ch
            elif cho and jung is None:
                result.append(cho)
                cho = ch
            elif cho and jung and jong is None:
                #겹받침 판단
                if i + 1 < len(line):
                    next_ch = line [i +1]
                    if determine(next_ch) == 'jaeum' and (ch, next_ch) in COMPOSED_JONG:
                        if i + 2 < len(line) and determine(line[i+2]) == 'moeum':
                            jong = ch
                            i += 1
                        else:
                            jong = COMPOSED_JONG[(ch, next_ch)]
                            i += 2
                        continue
                jong = ch
            elif cho and jung and jong:
                result.append(combine_hangul(cho, jung, jong))
                cho, jung, jong = ch, None, None
            i += 1
            continue

        elif ch_type == 'moeum':
            # 이중모음 조합 먼저 체크
            if jung and jong is None and (jung, ch) in COMPOSED_JUNG:
                jung = COMPOSED_JUNG[(jung, ch)]
                i += 1
                continue
            # 일반 모음 처리
            if cho and jung and jong:
                result.append(combine_hangul(cho, jung))
                if jong in CHOSUNG_LIST:
                    cho = jong
                else:
                    result.append(jong)
                    cho = None
                jung, jong = ch, None
            elif cho and jung is None:
                jung = ch
            elif cho and jung:
                result.append(combine_hangul(cho, jung))
                cho, jung, jong = None, ch, None
            elif not cho:
                jung = ch
            i += 1
            continue

        # 숫자나 기타 기호 처리
        else:
            if cho and jung and jong:
                result.append(combine_hangul(cho, jung, jong))
            elif cho and jung:
                result.append(combine_hangul(cho, jung))
            elif cho:
                result.append(cho)
            elif jung:
                result.append(jung)
            cho, jung, jong = None, None, None
            result.append(ch)
            i += 1
            continue

    # 마지막 글자 처리
    if cho and jung and jong:
        result.append(combine_hangul(cho, jung, jong))
    elif cho and jung:
        result.append(combine_hangul(cho, jung))
    elif cho:
        result.append(cho)
    elif jung:
        result.append(jung)

    print("결과:", ''.join(result))

def main():
    print("띄어쓰기 없이 자음, 모음을 입력하고 enter를 누르세요. 종료하려면 Ctrl+C를 누르세요.")
    try:
        while True:
            line = input("입력: ")
            make_hangul(line)
    except KeyboardInterrupt:
        print("\n한글 오토마타 종료")

if __name__ == "__main__":
    main()
