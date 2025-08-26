import serial
import time


class CBDTL:
    def __init__(self, meter_NO, prot="COM3", baudrate=2400, parity=serial.PARITY_EVEN, timeout=1):
        self.port = prot
        self.baudrate = baudrate
        self.parity = parity
        self.timeout = timeout
        self.meterno = meter_NO
        self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, parity=self.parity, timeout=self.timeout)
        self.frame = bytearray([0x68])

    def gen_start_frame(self):
        self.frame.clear()
        self.frame.append(0x68)
        metercod_str = self.format_and_transform_string(self.meterno)
        # 地址
        for item in metercod_str:
            self.frame.append(int(item, 16))
        # 起始符
        self.frame.append(0x68)
        # 控制码
        self.frame.append(0x11)
        # 数据长度
        self.frame.append(0x04)



    def gen_verification_code_adn_add_after_cod(self):
        frame = self.frame
        # 计算校验码
        jy_sum = 0
        for bain in frame:
            jy_sum += bain  # 直接使用bain而不是int(bain, 10)

        jy_code = jy_sum % 256  # 直接取模得到校验和
        frame.append(jy_code)

        frame.append(0x16)  # 帧尾
        hex_string = frame.hex()
        print(hex_string,"输出16进制字符串")  # 输出16进制字符串
        print(frame,"输出比特位")
        for i in frame:
            print(i,type(i))

    def meter_reading_active_power(self):#读取有功电量
        self.gen_start_frame()
        # 数据域/数据标识(DI0-DI3)
        self.frame.append(0x33)
        self.frame.append(0x33)
        self.frame.append(0x33)
        self.frame.append(0x33)
        self.gen_verification_code_adn_add_after_cod()
        str_response = self.read_handler()
        print(str_response,"response")
        nth1_code = str_response[-20:-4]
        meter_amount = self.gen_formatting_data(nth1_code) /100
        final_dic = {"meter_no":self.meterno,"val":meter_amount,"unit":"kWh","explain":"有功电量"}
        print(final_dic)
        return final_dic

    def check_meterNo_handler(self,code):
        nth1code = code.split('68')
        orgin_rev_meterNo = nth1code[1]
        pass

    def meter_reading_A_phase_voltage(self):#读取A相电压
        self.gen_start_frame()
        # 数据域/数据标识(DI0-DI3)
        self.frame.append(0x33)
        self.frame.append(0x34)
        self.frame.append(0x34)
        self.frame.append(0x35)
        self.gen_verification_code_adn_add_after_cod()
        str_response = self.read_handler()
        val =  self.gen_formatting_data(str_response[-6:-4]) / 10
        final_dic = {"meter_no": self.meterno, "val": val, "unit": "V","explain":"A相电压"}
        print(final_dic)
        return final_dic
    def meter_reading_voltage(self):#读取电压
        self.gen_start_frame()
        # 数据域/数据标识(DI0-DI3)
        self.frame.append(0x35)
        self.frame.append(0x34)
        self.frame.append(0x32)
        self.frame.append(0x33)
        self.gen_verification_code_adn_add_after_cod()
        str_response = self.read_handler()
        val =  self.gen_formatting_data(str_response[-14:-4]) / 10
        final_dic = {"meter_no": self.meterno, "val": val, "unit": "V","explain":"电压"}
        print(final_dic)
        return final_dic

    def read_handler(self):
        print(self.frame,"发送的数据")
        # return
        self.ser.write(self.frame)
        time.sleep(1)  # 等待响应
        # 读取返回数据
        response = self.ser.read(self.ser.in_waiting or 1)  # 读取缓冲区数据
        str_response = response.hex()

        if str_response.split("68")[2][3:4]=="1":
            raise Exception("错误")
        return str_response

    def meter_reading_A_phase_electric(self):#读取A相电流
        self.gen_start_frame()
        # 数据域/数据标识(DI0-DI3)
        self.frame.append(0x33)
        self.frame.append(0x34)
        self.frame.append(0x35)
        self.frame.append(0x35)
        self.gen_verification_code_adn_add_after_cod()
        str_response = self.read_handler()
        val =  self.gen_formatting_data(str_response[-6:-4]) / 1000
        final_dic = {"meter_no": self.meterno, "val": val, "unit": "A","explain":"A相电流"}
        print(final_dic)
        return final_dic

    def meter_reading_A_phase_power(self):#读取A相有功功率
        self.gen_start_frame()
        # 数据域/数据标识(DI0-DI3)
        self.frame.append(0x33)
        self.frame.append(0x34)
        self.frame.append(0x36)
        self.frame.append(0x35)
        self.gen_verification_code_adn_add_after_cod()
        str_response = self.read_handler()
        val = self.gen_formatting_data(str_response[-6:-4]) / 10000
        final_dic = {"meter_no": self.meterno, "val": val, "unit": "kW", "explain": "A相有功功率"}
        print(final_dic)
        return final_dic


    def gen_formatting_data(self,val):
        pairs = ([val[i:i + 2] for i in range(0, len(val), 2)])[::-1]
        target_value = "0"
        for items in pairs:
            temp = int(f"0x{items}", 16)
            target_value += str(hex(temp - 0x33))[2:]
        if int(target_value) != 0:
            target_value = int(target_value.lstrip('0').rstrip('0'))
        return target_value



    def format_and_transform_string(self,s):
        # 1. 补零使字符串长度达到12
        s = s.zfill(12)

        # 2. 每两个字符一组拆分
        pairs = [s[i:i + 2] for i in range(0, len(s), 2)]

        # 3. 每组前面加上0x，并转换为字节
        alist =[]
        for pair in pairs:
            alist.append(pair)  # 转换为十进制并追加到bytearray中

        # 4. 反转bytearray
        alist.reverse()

        return alist

if __name__ == "__main__":
    try:
        # cb = CBDTL(meter_NO="2206701746")
        # cb = CBDTL(meter_NO="001803701347")
        # cb = CBDTL(meter_NO="2211022292")
        cb = CBDTL(meter_NO="999999999999")
        # cb.meter_reading_voltage()
        # cb.meter_reading_A_phase_voltage()
        cb.meter_reading_active_power()
        # cb.meter_reading_A_phase_electric()
        # cb.meter_reading_A_phase_power()
        print(sum(b'h\x92"\x02\x11"\x00h\x11\x043333') & 0xFF)
    except Exception as e:
        print(str(e))