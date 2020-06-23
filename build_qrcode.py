from qrcode.transport_key import TransportKey
from qrcode.transport_qrcode import QRCode, QRCodeParser
from qrcode.tag_len_value import TLV


def trans_data_to_dict(data):
    '''
    trans tlv format qrcode into human readable format
    :param data: tlv qrcode
    :return:
    '''
    output = []
    for tlv in data:
        if type(tlv.data).__name__ == 'list':
            output.append({tlv.label: trans_data_to_dict(tlv.data)})
        else:
            output.append({tlv.label: tlv.data})
    return output


if __name__  == '__main__':
    '''
    main function
    '''
    data = [
        TLV("51", "TWTV01"),
        TLV("52", [
            TLV("61", "1"),
            TLV("62", "Z"),
            TLV("63", "2"),
            TLV("64", "000000000000"),
            TLV("65", "00000000000000000000")
        ]),
        TLV("54", [
            TLV("41", "7"),
            TLV("42", "901350704"),
            TLV("44", "1"),
            TLV("45", "全票"),
            TLV("46", "9013507041588148301"),
        ]),
        TLV("55", [
            TLV("71", "街口帳戶"),
            TLV("72", "1"),
            TLV("73", "-60"),
            TLV("74", "20000"),
            TLV("75", "5000"),
            TLV("76", "20200526102503"),
        ])
    ]

    transport_key = TransportKey()

    qrcode = QRCode(data, transport_key)

    qrcode_parser = QRCodeParser(qrcode.data_hex_str_bytes_base64, transport_key)

    print('hex str: ', qrcode.data_hex_str_signed)
    print('hex str bytes: ', qrcode.data_hex_str_signed_bytes)
    print('base64 qrcode string: ', qrcode.data_hex_str_bytes_base64.decode("utf-8"))
    print('length: ', len(qrcode.data_hex_str_bytes_base64.decode("utf-8")))
    print('hex str bytes: ', qrcode_parser.qrcode_hex_str_bytes)
    print('hex str: ', qrcode_parser.qrcode_hex_str)

    print(trans_data_to_dict(qrcode_parser.decode_data))

    print(qrcode_parser.verify())




