from random import randint

def save_personal_best(waves_cleared, additional_damage):
    def encrypt(integer):
        string = ''
        for character in str(integer):
            string += {'0' : 'n', '1' : 'p', '2' : 'r', '3' : 't', '4' : 'v', '5' : 'x', '6' : 'z', '7' : 'b', '8' : 'd', '9' : 'f'}[character]
        string = chr(randint(98, 122)) + string + 'a'
        while len(string) < 20:
            string += chr(randint(97, 122))
        return string

    pb_file_name = 'pb.txt'
    
    with open(pb_file_name, 'w') as pb_file:
        pb_file.write(f'{encrypt(waves_cleared)}\n{encrypt(additional_damage)}')

def get_personal_best():
    def decrypt(string):
        string = string[1:string.index('a')]
        integer = ''
        for character in string:
            integer += {'n' : '0', 'p' : '1', 'r' : '2', 't' : '3', 'v' : '4', 'x' : '5', 'z' : '6', 'b' : '7', 'd' : '8', 'f' : '9'}[character]
        return int(integer)
    
    pb_file_name = 'pb.txt'

    try:
        with open(pb_file_name) as pb_file:
            waves_cleared, additional_damage = pb_file.readlines()
        return decrypt(waves_cleared), decrypt(additional_damage)

    except FileNotFoundError:
        return 0, 0