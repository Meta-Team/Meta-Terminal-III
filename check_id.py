import sys

if __name__ == '__main__':
    config_list = open(sys.argv[1], 'r').read().splitlines()
    motor_dict = {200 + i : '' for i in range(1, 12)}
    x200_list = [''] * 4
    x1FF_list = [''] * 4
    x2FF_list = [''] * 4
    for line in config_list:
        motor_type, motor_name, motor_id = line.split()
        motor_id = int(motor_id)
        rx_id = 0
        if motor_type == '3508' or motor_type == '2006':
            if motor_id > 8 or motor_id < 1:
                print('Invalid id for 3508: acceptable range: 1-8, receive: %d' % motor_id)
                break
            if motor_id <= 4:
                tx_id = motor_id - 1
                if x200_list[tx_id] == '':
                    x200_list[tx_id] = motor_name
                else:
                    print('tx id conflict: %s, %s' % (motor_name, x200_list[tx_id]))
                    break
            else:
                tx_id = motor_id - 5
                if x1FF_list[tx_id] == '':
                    x1FF_list[tx_id] = motor_name
                else:
                    print('tx id conflict: %s, %s' % (motor_name, x1FF_list[tx_id]))
                    break

            rx_id = 200 + motor_id

        elif motor_type == '3510':
            if motor_id > 3 or motor_id < 1:
                print('Invalid id for 3510: acceptable range: 1-3, receive: %d' % motor_id)
                break
            tx_id = motor_id - 1
            if x1FF_list[tx_id] == '':
                x1FF_list[tx_id] = motor_name
            else:
                print('tx id conflict: %s, %s' % (motor_name, x1FF_list[tx_id]))
                break

            rx_id = 204 + motor_id

        elif motor_type == '6020':
            if motor_id > 7 or motor_id < 1:
                print('Invalid id for 6020: acceptable range: 1-7, receive: %d' % motor_id)
                break
            if motor_id <= 4:
                tx_id = motor_id - 1
                if x1FF_list[tx_id] == '':
                    x1FF_list[tx_id] = motor_name
                else:
                    print('tx id conflict: %s, %s' % (motor_name, x1FF_list[tx_id]))
                    break
            else:
                tx_id = motor_id - 5
                if x2FF_list[tx_id] == '':
                    x2FF_list[tx_id] = motor_name
                else:
                    print('tx id conflict: %s, %s' % (motor_name, x2FF_list[tx_id]))
                    break

            rx_id = 204 + motor_id

        else:
            print('motor type unrecognized: %s' % motor_type)

        if rx_id == 0:
            break

        if not motor_dict[rx_id]:
            motor_dict[rx_id] = motor_name
        else:
            print('rx id conflict: %s, %s, %d' % (motor_name, motor_dict[rx_id], rx_id))
            break
    print('0x200:')
    print(x200_list)
    print('0x1FF:')
    print(x1FF_list)
    print('0x2FF:')
    print(x2FF_list)
    print('rx:')
    print(motor_dict)