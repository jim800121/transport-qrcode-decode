import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

from qrcode.tag_len_value import TLV


class QRCode:
    '''
    generate base64 qrcode string
    '''
    critical_data_tags = {'64', '53', '54', '55'}

    def __init__(self, data, transport_key):
        self.transport_key = transport_key
        self.data = data
        self.data_hex_str = self.get_hex_str(data)
        critical_data = self.get_critical_data(data)
        print("critical content: ", critical_data)
        critical_data = self.get_hex_str_bytes("".join(critical_data))
        signature = self.sign_citical_data(critical_data)
        self.insert_signature(signature)
        self.data_hex_str_signed = self.get_hex_str(self.data)
        self.data_hex_str_signed_bytes = self.get_hex_str_bytes(self.data_hex_str_signed)

        self.data_hex_str_bytes_base64 = self.get_hex_str_bytes_base64(self.data_hex_str_signed_bytes)

    def get_hex_str(self, data):
        hex_str = ""
        for tlv in data:
            hex_str += str(tlv)
        return hex_str

    def get_hex_str_bytes(self, data_hex_str):
        return bytes.fromhex(data_hex_str)

    def get_hex_str_bytes_base64(self, hex_str_bytes):
        return base64.b64encode(hex_str_bytes)

    def get_critical_data(self, data) -> list:
        '''
        find critical data from qrcode TLV structure
        :param data: qrcode TLV structure
        :return: critical data list
        '''
        critical_data = []
        for tlv in data:
            if tlv.label == '52':
                for sub_tlv in tlv.data:
                    if sub_tlv.label in self.critical_data_tags:
                        critical_data.append(str(sub_tlv))
            if tlv.label in self.critical_data_tags:
                critical_data.append(str(tlv))
        critical_data.sort()
        return critical_data

    def insert_signature(self, signature: bytes) -> None:
        '''
        find tag '52' and append block '65'(signature block)
        :param signature: bytes which signed by privateKey
        :return: None
        '''
        for tlv in self.data:
            if tlv.label == '52':
                tlv.data.append(
                    TLV('65', signature)
                )
                break

    def sign_citical_data(self, raw_data: bytes) -> bytes:
        '''
        use privateKey to sign critical data
        :param raw_data: critical data
        :return: signature
        '''
        if not raw_data:
            raise ValueError("raw data is None")
        # return rsa.sign(raw_data, privateKey, "SHA-256")
        return self.transport_key.privateKey.sign(raw_data, padding.PKCS1v15(), hashes.SHA256())


class QRCodeParser:
    '''
    parse base64 qrcode string
    '''

    def __init__(self, qrcode_b64, transport_key):

        # leaf tags
        self.leaf = ['51', [97, 104], [17, 43], [65, 74], [113, 159]]
        self.leaf_set = set()

        # signed tags
        self.critical_data_tags = {'64', '53', '54', '55'}
        self.critical_data_content = []

        self.decode_data = {

        }
        self.crypto = ""

        self.transport_key = transport_key
        self.qrcode_hex_str_bytes = base64.b64decode(qrcode_b64)
        self.qrcode_hex_str = self.qrcode_hex_str_bytes.hex()
        self.build()
        self.decode_data = self.tlv_parser(self.qrcode_hex_str)

    def build(self):
        '''
        generate leaf tags set
        :return:
        '''
        for x in self.leaf:
            if type(x).__name__ == 'list':
                for i in range(x[0], x[1]+1):
                    self.leaf_set.add(hex(i)[2:].zfill(2).upper())
            else:
                self.leaf_set.add(x)

    def hexstr_to_str(self, hexstr):
        return bytes.fromhex(hexstr).decode()

    def tlv_parser(self, tlv):
        data = []
        i = 0

        while i < len(tlv):
            t = tlv[i:i+2]
            dl_hex = tlv[i+2:i+4]
            dl = int(tlv[i+2:i+4], 16)
            extra_dl_len = 0
            if dl == 255:
                extra_dl_len = 4
                dl = int(tlv[i+4:i+8], 16)
                dl_hex += tlv[i+2:i+8]

            data_start = i + 4 + extra_dl_len
            data_end = i + 4 + extra_dl_len + 2 * dl
            if t == '65':
                self.crypto = bytes.fromhex(tlv[data_start:data_end])
                data.append(TLV(t, tlv[data_start:data_end]))
            elif t in self.leaf_set:
                data.append(TLV(t, self.hexstr_to_str(tlv[data_start:data_end])))
            else:
                data.append(TLV(t, self.tlv_parser(tlv[data_start:data_end])))
            if t in self.critical_data_tags:
                self.critical_data_content.append(tlv[i:data_end])
            i = data_end
        return data

    def verify(self):
        self.critical_data_content.sort()
        print("sign content: ", self.critical_data_content)
        self.critical_data_content = "".join(self.critical_data_content)
        self.critical_data_content = bytes.fromhex(self.critical_data_content)

        try:
            # if verify failed raise InvalidSignature Exception
            self.transport_key.publicKey.verify(self.crypto, self.critical_data_content, padding.PKCS1v15(), hashes.SHA256())
            return "Verify Status: Success"
        except InvalidSignature:
            return "Verify Status: Failed"
