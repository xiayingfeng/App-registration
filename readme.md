1. 根据实际情况重新给 account 与 password 赋值
2. driver path 是此文件夹中 chromedriver.exe 的路径
3. 由于该网站的反爬机制，会被拒绝访问，不能一次性爬完，需要分多次爬取，我目前设置的是每次 20 行，例如 ecl 中共有 111 项资源，因此 phase 的取值范围为[0, 6)，共运行 6 次，每运行一次修改一下 phase 的值，每次运行建议间隔 5~10min，最后会生成 phase 个文件，再手动把这些文件拼接一下再按照 display name 排序，最后将结果粘贴过去就是了
4. 每次运行需要 Authendicator 验证一下，如果你觉得验证时间不够，可以根据实际情况改，在 Main.py line53.
5. 如果不想看到浏览器，可以将 Main.py line34 取消注释
