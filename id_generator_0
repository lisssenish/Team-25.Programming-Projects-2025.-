import pandas as pd
names=pd.DataFrame(columns=['id','role','name','number'])#создание DataFrame для хранения id
def create_and_add_id(role,name):#функция для создания id
    roles_index={'Developer': 't', 'Administrator':'a','Manager': 'm', 'Shop':'s'}#словарь для определения буквенной переменной id
    k=roles_index[role] #буквенная переменная для id
    if len(names[names['role']==role]['number'])==0:#оператор для определения порядкового номера
        n=1
    else:
        n=max(names[names['role']==role]['number'])+1
    id=str(n)
    while len(id)<5:#цикл создания id
        id='0'+id
    id=k+id
    names.loc[len(names)] = [id, role, name, n]#добавление id в DataFrame


create_and_add_id('Developer','test1')
create_and_add_id('Shop','test2')
print(names)
output_file = 'id-base.xlsx' # Можно поменять расширение на .xlsx
