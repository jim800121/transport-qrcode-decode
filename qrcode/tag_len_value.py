class TLV:
    '''
    TLV object definition
    '''
    def __init__(self, label, data):
        self.label = label
        self.data = data

    def int_to_hexstr(self, i):
        if i > 254:
            return hex(i)[2:].zfill(4)
        return hex(i)[2:].zfill(2)

    def hexstr_to_int(self, hexstr):
        return int(hexstr, 16)

    def str_to_hexstr(self, s):
        return s.encode("utf-8").hex().upper()

    def hexstr_to_str(self, hexstr):
        return bytes.fromhex(hexstr).decode()

    def __str__(self):
        if type(self.data).__name__ == 'list':
            s = ""
            total = 0
            for tlv in self.data:
                s += str(tlv)
                total += len(tlv)
            if total > 254:
                return self.label + 'FF' + self.int_to_hexstr(total) + s
            return self.label + self.int_to_hexstr(total) + s
        else:
            dlen = 0
            output_data = ""
            if type(self.data).__name__ == 'str':
                dlen = len(self.data.encode("utf-8"))
                output_data = self.str_to_hexstr(self.data)
            elif type(self.data).__name__ == 'bytes':
                dlen = len(self.data)
                output_data = self.data.hex()
            else:
                raise TypeError
            if dlen > 254:
                return self.label + 'FF' + self.int_to_hexstr(dlen) + output_data
            return self.label + self.int_to_hexstr(dlen) + output_data

    def __len__(self):
        if type(self.data) == 'list':
            l = 0
            for tlv in self.data:
                print('label: ', tlv.label, len(tlv))
                l += len(tlv)
            return l + 2
        else:
            if type(self.data).__name__ == 'str':
                dlen = len(self.data.encode("utf-8"))
                if dlen > 254:
                    return dlen + 4
                return dlen + 2
            elif type(self.data).__name__ == 'bytes':
                dlen = len(self.data)
                if dlen > 254:
                    return dlen + 4
                return dlen + 2
            else:
                raise TypeError
