import pandas as pd 



fn = 'data/reviews_for_bert.csv'
df = pd.read_csv(fn)

for i, rev in enumerate(df['content'].to_list()):
    with open(f'data/reviews/{i}.txt', 'w') as f:
        f.writelines(rev)
    