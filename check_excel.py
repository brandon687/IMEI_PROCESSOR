import pandas as pd

df = pd.read_excel('/Users/brandonin/Downloads/claude code ex.xlsx')
print('Total rows:', len(df))
print('\nColumns:', list(df.columns))
print('\n' + '='*80)

for i in range(min(5, len(df))):
    print(f'\nRow {i+1}:')
    print(f"  SERVICE: {df.iloc[i]['SERVICE']}")
    print(f"  IMEI NO.: {df.iloc[i]['IMEI NO.']}")
    print(f"  STATUS: {df.iloc[i]['STATUS']}")
    print(f"  CODE: {df.iloc[i]['CODE']}")
    print(f"  CARRIER: {df.iloc[i]['CARRIER']}")
    print(f"  MODEL: {df.iloc[i]['MODEL']}")
