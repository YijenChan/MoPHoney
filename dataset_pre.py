import pandas as pd

# 读取CSV文件
file_path = r'shuffle_samples_hash.csv'
data = pd.read_csv(file_path)

# 删除空白行（即全空的行）
data = data.dropna(how='all')

# 保存到新文件
output_path = r'shuffle_samples_hash.csv'
data.to_csv(output_path, index=False)

# 打印记录数
print(f"记录总数：{len(data)}")
