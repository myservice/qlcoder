#!/usr/bin/python3
# http://www.qlcoder.com/task/7662

USER_TOTAL = 10000000

import math
import hashlib

users = [None] * USER_TOTAL
primeusers = [] # 素数用户列表。除了1以外的所有红人。
class User:
    '单个用户'
    __slots__ = [
        'id',
        'hot', # 指示是否是网络红人。红人的消息读扩散，非红人的消息写扩散
#        'following', # 关注的人。这个值没用。
        'follower', # 关注自己的人。如果自己不是红人，则发的信息投递到follower的inbox中。自己是红人，这个值没用。
        'hotfollowing', # 关注的网络红人(比自己小的那些)。需要从这些人的outbox中读取消息。每个元素是(id, outboxindex)。
        'prime_start', # 素数起始位置
        'bigger_prime_outboxindex', # 每个元素关注的比自己大的用户的outboxindex。
        'inbox', # 关注的人中非红人的更新投递到inbox
        'outbox', # 红人才有用，自己的更新列表
    ]
    
    def follow(self, id):
        tar = users[id - 1]
#        self.following.append(tar)
        if tar.hot:
            self.hotfollowing.append([tar, 0])
        else:
            tar.follower.append(self) #为了节省内存，目标是红人时不为其添加follower
    
    def __init__(self, id):
        self.id = id
        self.hot = False
#        self.following = []
        self.follower = []
        self.hotfollowing = []
        self.inbox = []
        self.outbox = []
        
        # 填充关注列表
        if id == 1:
            # 用户1关注所有用户，也被所有用户关注
#            self.following = users
            self.hot = True
        else:
            self.prime_start = len(primeusers)
            self.follow(1)
            is_prime = True
            max_test_value = int(math.sqrt(id))
            for i in range(2, max_test_value + 1):
                if id % i == 0:
                    is_prime = False
                    self.follow(i)
                    if id / i != i:
                        self.follow(int(id / i))
            if is_prime:
                self.hot = True
                primeusers.append(self)
                for user in users:
                    user.hotfollowing.append([self, 0])
            else:
                self.follower.append(users[0])
                    

    def post(self, msg):
        if self.hot:
            self.outbox.append(msg)
        else:
            for user in self.follower:
                user.inbox.append(msg)
                
    def view(self):
        temp = self.inbox
        self.inbox = []
        
        for data in self.hotfollowing:
            temp += data[0].outbox[data[1]:]
            data[1] = len(data[0].outbox)
        def getindex(msg):
            return msg[0]
        temp.sort(key = getindex)
        
        temp.reverse()
        temp = [msg[1] for msg in temp]
        return '-'.join(temp)

url = 'http://121.201.63.168/uploads/145813004658861.py'
filename = 'temp_7665.py'
DATA_FILE = 'temp_7665_data.txt'
__import__('util').loadfile(url, filename)

import os
if not os.path.isfile(DATA_FILE):
    print('生成数据文件……')
    os.system('python {}'.format(filename))
    os.rename('timeline.txt', DATA_FILE)
else:
    print('数据文件早已准备好')

print('初始化用户……')
for i in range(1, USER_TOTAL + 1):
    users.append(User(i))
    if i % 100000 == 0:
        print('已创建{}万个用户'.format(int(i / 10000)))

print('处理行为……')
data = open(DATA_FILE)
resultmd5 = None
lineindex = 0

for line in data:
    temp = line.split(' ')
    user = users[int(temp[1]) - 1]
    if temp[0] == 'p':
        msg = (lineindex, temp[2][:-1])
        user.post(msg)
    else:
        view = user.view()
        linemd5 = hashlib.md5(view.encode()).hexdigest()
        if resultmd5 is None:
            resultmd5 = hashlib.md5(linemd5.encode())
        else:
            resultmd5.update(('-' + linemd5).encode())
        
    lineindex += 1
    
    if lineindex % 100000 == 0:
        print('已处理{}万条记录'.format(int(lineindex / 10000)))

print('答案是', resultmd5.hexdigest())
