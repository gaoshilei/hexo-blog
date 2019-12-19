import os
import sys
import os.path
import shutil

def main():
    # os.getcwd() 方法用于返回当前工作目录

    print('\n')
    current_path = os.getcwd()
    file_list = get_files(current_path)  
    replace_img_host(file_list)

#获取当前目录下所有md文件
def get_files(dir_path):
    print('当前所在路径：' + dir_path + '\n')
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if '.md' in file:
                file_list.append(dir_path + '/' + file)
            else:
                continue
        break
    return file_list

#替换所有图片的host
def replace_img_host(file_list):
	for file_path in file_list:
		replace_img_host_single_file(file_path)

#处理单个文件
def replace_img_host_single_file(file_path):
	print('\n开始处理文件：\n' + file_path)
	read_file_handle = open(file_path)
	file_content = read_file_handle.read()
	read_file_handle.close()

	file_content_row_list = file_content.split('\n')
	new_file_content = ''

	for row in file_content_row_list:
		if 'http://www.leonlei.top' in row:
			# print('找到匹配字符串：')
			# print(row)
			# row.replace('www.leonlei.top','img.gaoshilei.com')
			list = row.split('http://www.leonlei.top')
			row = 'http://img.gaoshilei.com'.join(list)
			print('被修改的row：' + row)
		if new_file_content == '':
			new_file_content = row
		else:
			new_file_content = new_file_content + '\n' + row

	write_file_Handle = open(file_path,'w')
	print('写入文件：' + file_path)
	write_file_Handle.write(new_file_content)
	write_file_Handle.close()


if __name__ == '__main__':
    main()