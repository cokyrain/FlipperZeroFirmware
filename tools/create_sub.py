#!/usr/bin/env python3 https://gist.github.com/jinschoi/f39dbd82e4e3d99d32ab6a9b8dfc2f55

from typing import Iterable, Union, Any

# freq: frequency in Hz
# zerolen: length of space bit in μs
# onelen: length of mark bit in μs
# repeats: number of times to repeat sequence
# pause: time to wait in μs between sequences
# bits: string of ones and zeros to represent sequence

def gen_sub(freq, zerolen, onelen, repeats, pause, bits):
    res = f"""Filetype: Flipper SubGhz RAW File
Version: 1
Frequency: {freq}
Preset: FuriHalSubGhzPresetOok650Async
Protocol: RAW
"""
    if pause == 0:
        # Pause must be non-zero.
        pause = zerolen

    data = []
    prevbit = None
    prevbitlen = 0
    for bit in bits:
        if prevbit and prevbit != bit:
            data.append(prevbitlen)
            prevbitlen = 0

        if bit == '1':
            prevbitlen += onelen
        else:
            prevbitlen -= zerolen

        prevbit = bit

    if prevbit == '1':
        data.append(prevbitlen)
        data.append(-pause)
    else:
        data.append(prevbitlen - pause)

    datalines = []
    for i in range(0, len(data), 512):
        batch = [str(n) for n in data[i:i+512]]
        datalines.append(f'RAW_Data: {" ".join(batch)}')
    res += '\n'.join(datalines)

    return res

# From Wikipedia
def de_bruijn(k: Union[Iterable[Any], int], n: int) -> str:
    """de Bruijn sequence for alphabet k
    and subsequences of length n.
    """
    # Two kinds of alphabet input: an integer expands
    # to a list of integers as the alphabet..
    if isinstance(k, int):
        alphabet = list(map(str, range(k)))
    else:
        # While any sort of list becomes used as it is
        alphabet = k
        k = len(k)

    a = [0] * k * n
    sequence = []

    def db(t, p):
        if t > n:
            if n % p == 0:
                sequence.extend(a[1 : p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)

    db(1, 1)
    return "".join(alphabet[i] for i in sequence)

def debruijn(freq, zerolen, onelen, encoding, bitlen, alphabet=2):
    def encode(bit):
        return encoding[bit]
    return gen_sub(freq, zerolen, onelen, 1, 0, ''.join(encode(b) for b in de_bruijn(alphabet, bitlen)))

TOUCH_TUNES_COMMANDS = {'On_Off': 0x78,
                        'Pause': 0x32, #0xB3,
                        'P1': 0x70, #0xF1,
                        'P2_Edit_Queue': 0x60,
                        'P3_Skip': 0xCA,
                        'F1_Restart': 0x20,
                        'F2_Key': 0xA0,
                        'F3_Mic_A_Mute': 0x30,
                        'F4_Mic_B_Mute': 0xB0,
                        'Mic_Vol_Plus_Up_Arrow': 0xF2,
                        'Mic_Vol_Minus_Down_Arrow': 0x80,
                        'A_Left_Arrow': 0x84,
                        'B_Right_Arrow': 0xC4,
                        'OK': 0x44, #0xDD,
                        'Music_Vol_Zone_1Up': 0xD0, #0xF4,
                        'Music_Vol_Zone_1Down': 0x50,
                        'Music_Vol_Zone_2Up': 0x90, #0xF6,
                        'Music_Vol_Zone_2Down': 0x10,
                        'Music_Vol_Zone_3Up': 0xC0, #0xFC,
                        'Music_Vol_Zone_3Down': 0x40,
                        '1': 0xF0,
                        '2': 0x08,
                        '3': 0x88,
                        '4': 0x48,
                        '5': 0xC8,
                        '6': 0x28,
                        '7': 0xA8,
                        '8': 0x68,
                        '9': 0xE8,
                        '0': 0x98,
                        'Music_Karaoke(*)': 0x18,
                        'Lock_Queue(#)': 0x58}

def encode_touchtunes(command, pin=0x00):
    #Syncword
    frame = 0x5D

    #PIN
    for bit in range(8):
        frame <<= 1
        if pin&(1<<bit):
            frame |= 1
    #Insert button code and it's complement
    frame <<= 16
    frame |= (command << 8)
    frame |= (command ^ 0xFF)

    #Convert to raw signal
    #0 symble == 10 && 1 symble == 1000
    ook = ""
    for i in range(8+8+16):
        if (frame & 0x80000000):
            ook +="1000"
            frame <<=1
        else:
            ook += "10"
            frame <<=1
    return "1"*16 + "0"*8 + ook + "1000"


if __name__ == '__main__':
    # https://github.com/samyk/opensesame/blob/48b7d25c9d7aa3e2ac5cadfdcb2db1c78e001565/garages.h
    with open('10bit-310mhz.sub', 'w') as f:
        print(debruijn(310000000, 500, 500, {'0': '1000', '1': '1110'}, 10), file=f)
    with open('9bit-390mhz.sub', 'w') as f:
        print(debruijn(390000000, 500, 500, {'0': '1000', '1': '1110'}, 9), file=f)
    with open('9bit-315mhz.sub', 'w') as f:
        print(debruijn(315000000, 500, 500, {'0': '1000', '1': '1110'}, 9), file=f)
    with open('10bit-300mhz.sub', 'w') as f:
        print(debruijn(300000000, 500, 500, {'0': '1000', '1': '1110'}, 10), file=f)
    with open('nscd.sub', 'w') as f:
        print(debruijn(318000000, 500, 500, {'0': '100000000100000000',
                                             '1': '111111110100000000',
                                             '2': '111111110111111110'}, 9, alphabet=3), file=f)

    # https://github.com/jimilinuxguy/Tesla-Charging-Port-Opener
    with open('tesla.sub', 'w') as f:
        print(gen_sub(315000000, 400, 400, 10, 25562, '101010101010101010101010100010101100101100110010110011001100110011001011010011010010110101001010110100110100110010101011010010110001010110010110011001011001100110011001100101101001101001011010100101011010011010011001010101101001011000101011001011001100101100110011001100110010110100110100101101010010101101001101001100101010110100101'), file=f)

    
    # Touch Tunes jukebox (https://github.com/notpike/The-Fonz/blob/master/The_Fonz.py)
    pin = 0
    for cmdname, cmd in TOUCH_TUNES_COMMANDS.items():
        with open(cmdname + '.sub', 'w') as f:
            print(gen_sub(433920000, 566, 566, 1, 0, encode_touchtunes(cmd, pin)), file=f)
