



# wangsixue 142 30
# zhaominghao 140 32
# zhangsan 150 30
# lisi 140 30
# wangwu 140 30


int a , b, c, d, e; 
int a1, b1, c1, d1, e1;
a = 142;
b = 140;
c = 150;
d = 140;
e = 140;
a1 = 30;
b1 = 32;
c1 = 30;
d1 = 30;
e1 = 30;
int maxn = -1e9;
int maxn1 = -1e9;
maxn = max(maxn, a);
maxn = max(maxn, b);
maxn = max(maxn, c);
maxn = max(maxn, d);
maxn = max(maxn, e);
maxn1 = max(maxn1, a1);
maxn1 = max(maxn1, b1);
maxn1 = max(maxn1, c1);
maxn1 = max(maxn1, d1);
maxn1 = max(maxn1, e1);
if(maxn == a){
    print("wangsixue");
}
else if(maxn == b){
    print("zhaominghao");
}
else if(maxn == c){
    print("zhangsan");
}
else if(maxn == d){
    print("lisi");
}
else if(maxn == e){
    print("wangwu");
}
if(maxn1 == a1){
    print("wangsixue");
}
else if(maxn1 == b1){
    print("zhaominghao");
}
else if(maxn1 == c1){
    print("zhangsan");
}
else if(maxn1 == d1){
    print("lisi");
}
else if(maxn1 == e1){
    print("wangwu");
}

# 找出最重的人参加铅球比赛

#找出最高的人参加跳高比赛