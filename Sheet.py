import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

class GSdata():
    scope = ["https://spreadsheets.google.com/feeds",
    'https://www.googleapis.com/auth/spreadsheets',
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("GoodsManager.json", scope)


    def __init__(self,product_name = 'Sheet1'):

        self.ManagerName_cell = 'C4'
        self.place_cell = 'C6'
        self.product_name_cell = 'C8'
        self.tax_indentity_cell = 'F5'
        self.Datetime = datetime.now().strftime("%Y-%m-%d")
        self.gc = gspread.authorize(GSdata.creds)
        self.sheet = self.gc.open('GOODS2')

        ### loop to find desire worksheet
        self.worksheet = self.sheet.worksheets()

        self.product_name = product_name

        if self.__Check_existing():
            Feedback = 'ไม่มี Product {} อยู่ขณะนี้ ทำการสร้างตารางใหม่ ?(y/n)'.format(self.product_name)
            Input = input(Feedback)
            if Input == 'y':
                self.create_stock()
            else :
                print('Good Luck')


        ## check if product exist or not
    def __Check_existing(self):
        for i in self.worksheet:
            print(i.title)
            if i.title == self.product_name:
                self.worksheet = self.sheet.worksheet(i.title)
                return False
        return True


        ## create new worksheet
    def create_stock(self,Manager_name = 'Pybott',address_name= 'bangkok',tax_iden= '10010'):

        self.sheet.worksheet('Sheet1').duplicate(new_sheet_name = self.product_name)
        ## set current worksheet
        self.worksheet = self.sheet.worksheet(self.product_name)

        self.worksheet.update_acell(self.ManagerName_cell,Manager_name)

        self.worksheet.update_acell(self.place_cell,address_name)

        self.worksheet.update_acell(self.product_name_cell,self.product_name)

        self.worksheet.update_acell(self.tax_indentity_cell,tax_iden)


        ## add new incoming data
    def add_product_data(self,number_of_item ,product_number , method = 'รับ',note = None):
        values_list = self.worksheet.col_values(2)
        current_row = len(values_list) + 1

        current_row_num = 'B'+str(current_row)
        self.worksheet.update_acell(current_row_num,product_number)

        current_row_date = 'C'+str(current_row)
        self.worksheet.update_acell(current_row_date,self.Datetime)


        if method == 'รับ':
            current_row_receive = 'D'+str(current_row)
            self.worksheet.update_acell(current_row_receive,number_of_item)

        else :
            current_row_dis = 'E'+str(current_row)
            self.worksheet.update_acell(current_row_dis,number_of_item)
        
        if note is not None:
            current_row_note = 'G'+str(current_row)
            self.worksheet.update_acell(current_row_note,note)

        return 'You have updated your products amount'
    

    # ลบสินค้า 
    def delete_product_data(self,product_number):
        cell = self.worksheet.find(str(product_number))
        current_row_num = 'B'+str(cell.row)
        self.worksheet.update_acell(current_row_num,'')

        current_row_date = 'C'+str(cell.row)
        self.worksheet.update_acell(current_row_date,'')

        current_row_receive = 'D'+str(cell.row)
        self.worksheet.update_acell(current_row_receive,'')

        current_row_dis = 'E'+str(cell.row)
        self.worksheet.update_acell(current_row_dis,'')

        current_row_note = 'G'+str(cell.row)
        self.worksheet.update_acell(current_row_note,'')


        return 'You have delete your products amount'



if __name__ == '__main__':
    #from Sheet import GSdata

    ## ทำการสร้าง worksheet ใหม่ ของสินค้าชื่อ Book
    new_prod = GSdata('Book') 
    ## บันทึกข้อมูล หนังสือใน worksheet book
    new_prod.add_product_data('5','1002030','รับ','หนังสือจากPybott')
    ## บันทึกข้อมูล หนังสือใน worksheet book
    new_prod.add_product_data('5','1005599','รับ','หนังสือจากPybott2') 
    ## บันทึกข้อมูล หนังสือใน worksheet book
    new_prod.add_product_data('5','1005588','จ่าย','หนังสือจากPybott2') 
    ## ทำการลบข้อมูลออก ตามเลข ที่ใส่เข้าไป
    new_prod.delete_product_data('1005599')



    
    

        

