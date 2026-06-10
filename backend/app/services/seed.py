from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.entities import Category, Favorite, Item, Message, User


DEFAULT_CATEGORIES = [
    "教材",
    "数码",
    "生活用品",
    "运动户外",
    "宿舍电器",
    "学习办公",
    "出行代步",
    "乐器周边",
]

DEFAULT_USERS = [
    {
        "username": "demo",
        "password": "123456",
        "role": "student",
        "status": "active",
        "phone": "18800000000",
        "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=200&q=80",
    },
    {
        "username": "xiaolin",
        "password": "123456",
        "role": "student",
        "status": "active",
        "phone": "18800000001",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=200&q=80",
    },
    {
        "username": "chenxi",
        "password": "123456",
        "role": "student",
        "status": "active",
        "phone": "18800000002",
        "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80",
    },
    {
        "username": "yuhan",
        "password": "123456",
        "role": "student",
        "status": "active",
        "phone": "18800000003",
        "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=200&q=80",
    },
    {
        "username": "jiaqi",
        "password": "123456",
        "role": "student",
        "status": "active",
        "phone": "18800000004",
        "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=200&q=80",
    },
    {
        "username": "admin",
        "password": "123456",
        "role": "admin",
        "status": "active",
        "phone": "18800000999",
        "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80",
    },
]

IMAGE_POOL = {
    "教材": [
        "https://images.unsplash.com/photo-1769794371055-54436b54577e?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1749631951548-c26612825aed?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=80",
    ],
    "数码": [
        "https://images.unsplash.com/photo-1743862558309-d3e9da38404c?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1674036373727-50eb89eed019?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?auto=format&fit=crop&w=900&q=80",
    ],
    "生活用品": [
        "https://images.unsplash.com/photo-1652517040343-360ac37e099b?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=900&q=80",
    ],
    "运动户外": [
        "https://images.unsplash.com/photo-1741252462304-388382a88f6e?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1721760886982-3c643f05813d?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1546519638-68e109498ffc?auto=format&fit=crop&w=900&q=80",
    ],
    "宿舍电器": [
        "https://images.unsplash.com/photo-1517414467812-ef3dbd81859a?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1585771724684-38269d6639fd?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?auto=format&fit=crop&w=900&q=80",
    ],
    "学习办公": [
        "https://images.unsplash.com/photo-1769794371055-54436b54577e?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1749631951548-c26612825aed?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=900&q=80",
    ],
    "出行代步": [
        "https://images.unsplash.com/photo-1590092940833-0af304b36ee7?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1517949908118-721d3f81fd93?auto=format&fit=crop&w=900&q=80",
    ],
    "乐器周边": [
        "https://images.unsplash.com/photo-1770816855630-9c4d6e821126?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1511379938547-c1f69419868d?auto=format&fit=crop&w=900&q=80",
    ],
}

ITEM_TEMPLATES = {
    "教材": [
        ("高等数学教材（同济版）", "课后题有少量铅笔标记，适合大一复习。", 18, 58, "good", "on_sale"),
        ("Python 程序设计基础", "封面完整，附课堂笔记整理。", 22, 69, "good", "on_sale"),
        ("大学英语四六级词汇书", "划重点清晰，背词复习都方便。", 10, 35, "fair", "on_sale"),
        ("离散数学学习指导", "题型全，适合人工智能专业打基础。", 15, 42, "good", "reserved"),
        ("线性代数教材", "书页干净，适合期末冲刺。", 14, 39, "good", "on_sale"),
        ("数据结构习题解析", "刷题用书，边角有轻微磨损。", 16, 45, "fair", "on_sale"),
        ("概率论与数理统计", "老师推荐版本，内容完整。", 17, 48, "good", "on_sale"),
        ("人工智能导论参考书", "章节很全，适合课程配套学习。", 25, 78, "good", "reserved"),
        ("考研数学真题册", "只做了前几套，剩余内容几乎全新。", 20, 55, "new", "on_sale"),
        ("机器学习入门笔记合集", "自己打印装订，知识点总结清楚。", 12, 30, "good", "on_sale"),
    ],
    "数码": [
        ("蓝牙机械键盘", "支持蓝牙和有线双模，宿舍自用后转出。", 120, 299, "good", "reserved"),
        ("无线鼠标", "静音按键，适合图书馆和自习室。", 35, 89, "good", "on_sale"),
        ("二手 iPad 保护壳", "尺寸适配 10.2 英寸，轻微使用痕迹。", 18, 49, "fair", "on_sale"),
        ("Type-C 扩展坞", "日常接显示器和 U 盘都没问题。", 46, 119, "good", "on_sale"),
        ("头戴式耳机", "音质稳定，通勤和宿舍都适用。", 88, 219, "good", "on_sale"),
        ("便携充电宝 20000mAh", "电量健康，支持双口输出。", 52, 129, "good", "reserved"),
        ("旧款显示器支架", "桌面空间更整洁，安装方便。", 40, 99, "fair", "on_sale"),
        ("USB 麦克风", "开会和做展示录音够用。", 68, 168, "good", "on_sale"),
        ("宿舍路由器", "信号稳定，已恢复出厂设置。", 39, 109, "fair", "sold"),
        ("平板电容笔", "做笔记顺手，续航正常。", 56, 149, "good", "on_sale"),
    ],
    "生活用品": [
        ("加厚收纳箱", "容量大，适合宿舍换季收纳。", 20, 49, "good", "on_sale"),
        ("宿舍落地衣架", "稳固耐用，拆装方便。", 28, 69, "good", "on_sale"),
        ("保温饭盒", "密封性不错，带去实验室很方便。", 18, 45, "good", "reserved"),
        ("折叠小书桌", "床上学习够用，表面平整。", 32, 88, "fair", "on_sale"),
        ("寝室台灯", "亮度三档可调，夜晚复习不刺眼。", 24, 59, "good", "on_sale"),
        ("简约镜子", "放桌面或挂墙都可以。", 12, 29, "new", "on_sale"),
        ("抱枕靠垫", "午休和宿舍追剧都舒服。", 15, 39, "good", "on_sale"),
        ("水杯套装", "有两只杯子，适合室友一起用。", 14, 35, "fair", "sold"),
        ("宿舍门后挂钩", "免打孔，收纳包和外套很实用。", 9, 22, "new", "on_sale"),
        ("简易洗衣篮", "轻便耐脏，搬去洗衣房很方便。", 11, 28, "good", "on_sale"),
    ],
    "运动户外": [
        ("羽毛球拍一对", "拍线状态不错，适合社团活动和约球。", 66, 168, "fair", "on_sale"),
        ("篮球 7 号", "气密性正常，球场日常训练可用。", 38, 99, "good", "on_sale"),
        ("瑜伽垫", "厚度适中，宿舍健身很方便。", 25, 69, "good", "reserved"),
        ("跳绳计数款", "握把舒服，体育测试前冲一波。", 16, 39, "new", "on_sale"),
        ("折叠露营椅", "周末出游或者操场看比赛都能用。", 45, 118, "good", "on_sale"),
        ("运动护膝", "尺寸适中，慢跑和打球都可用。", 20, 52, "good", "on_sale"),
        ("哑铃一对 5kg", "适合宿舍简单力量训练。", 58, 138, "fair", "on_sale"),
        ("足球鞋", "42 码，鞋钉磨损不明显。", 73, 199, "good", "sold"),
        ("骑行头盔", "卡扣正常，外壳有轻微划痕。", 30, 89, "fair", "on_sale"),
        ("便携运动水壶", "容量大，操场训练带着方便。", 12, 32, "new", "on_sale"),
    ],
    "宿舍电器": [
        ("宿舍小风扇", "风力有三档，夏天学习很实用。", 28, 79, "good", "on_sale"),
        ("迷你加湿器", "静音运行，晚上睡觉也能开。", 19, 55, "good", "on_sale"),
        ("电热水壶", "烧水快，保温功能正常。", 36, 99, "good", "reserved"),
        ("台式小夜灯", "亮度柔和，适合晚自习后用。", 14, 35, "new", "on_sale"),
        ("宿舍吹风机", "冷热风切换正常。", 32, 89, "fair", "on_sale"),
        ("便携榨汁杯", "电池续航正常，适合早八带果汁。", 48, 129, "good", "on_sale"),
        ("USB 暖手垫", "冬天打字不冻手。", 16, 42, "new", "on_sale"),
        ("桌面吸尘器", "清理键盘和桌面碎屑很方便。", 21, 58, "good", "on_sale"),
        ("寝室卷发棒", "升温快，已消毒清洁。", 27, 76, "fair", "sold"),
        ("插线板带 USB", "接口够用，适合床边和书桌。", 18, 46, "good", "on_sale"),
    ],
    "学习办公": [
        ("文件收纳架", "桌面整理利器，资料不再乱放。", 14, 36, "good", "on_sale"),
        ("A4 打印纸一包", "还剩大半包，课程设计够用。", 12, 25, "new", "on_sale"),
        ("白板记号笔套装", "颜色齐全，开组会讲方案方便。", 10, 28, "good", "on_sale"),
        ("计算器", "考试常用型号，按键灵敏。", 26, 69, "good", "reserved"),
        ("文件夹三件套", "课程资料分类很好用。", 9, 22, "new", "on_sale"),
        ("桌面番茄钟", "学习计时效率高，转起来很顺。", 18, 49, "good", "on_sale"),
        ("打孔器", "做展示材料或整理文件很方便。", 13, 35, "fair", "on_sale"),
        ("桌面日历便签", "复习安排和截止日期一目了然。", 8, 19, "new", "on_sale"),
        ("U 盘 64G", "传课件和实验报告都够用。", 29, 79, "good", "sold"),
        ("便携笔记本支架", "上网课抬高视线很舒服。", 24, 65, "good", "on_sale"),
    ],
    "出行代步": [
        ("二手自行车锁", "密码锁好用，日常通勤够稳。", 18, 49, "good", "on_sale"),
        ("自行车前灯", "夜骑亮度够用，充电正常。", 22, 59, "good", "on_sale"),
        ("电动车头盔", "校内通勤常用，内衬干净。", 36, 96, "good", "reserved"),
        ("便携雨衣", "书包里常备，突然下雨不慌。", 11, 28, "new", "on_sale"),
        ("车篮挂钩", "买菜或拿快递时特别方便。", 7, 16, "new", "on_sale"),
        ("手机导航支架", "固定稳定，骑车看地图更安全。", 15, 39, "good", "on_sale"),
        ("自行车打气筒", "气压够，宿舍楼下就能补胎。", 19, 48, "fair", "on_sale"),
        ("折叠雨伞", "伞骨完整，适合放书包。", 10, 25, "good", "sold"),
        ("反光臂带", "夜跑和夜骑更安全。", 8, 18, "new", "on_sale"),
        ("简易修车工具包", "内含撬胎棒和内六角。", 27, 68, "good", "on_sale"),
    ],
    "乐器周边": [
        ("民谣吉他背带", "承重稳定，调节长度方便。", 18, 45, "good", "on_sale"),
        ("吉他调音器", "夹式调音灵敏，排练前很好用。", 20, 56, "good", "on_sale"),
        ("入门尤克里里", "音准正常，适合新手练手。", 78, 189, "fair", "reserved"),
        ("电子节拍器", "练琴节奏更稳。", 24, 59, "good", "on_sale"),
        ("琴谱架", "折叠收纳方便，社团演出可用。", 30, 85, "good", "on_sale"),
        ("降噪耳塞", "排练或舞台边使用都合适。", 12, 31, "new", "on_sale"),
        ("吉他拨片一盒", "里面有多种厚度，几乎全新。", 9, 20, "new", "on_sale"),
        ("电钢琴踏板", "接口正常，响应灵敏。", 35, 88, "good", "sold"),
        ("小型音箱连接线", "排练时备用很实用。", 16, 42, "fair", "on_sale"),
        ("麦克风支架", "结构稳定，适合宿舍录歌。", 42, 109, "good", "on_sale"),
    ],
}

MESSAGE_TEMPLATES = [
    "支持校内当面交易，今晚图书馆附近也可以。",
    "如果你方便的话，可以中午在食堂门口看实物。",
    "价格还能小刀一点，真心想要可以聊聊。",
    "这件商品我自己一直在用，功能都正常。",
    "宿舍楼下或者教学楼都能面交，时间比较灵活。",
]


def ensure_users(db: Session):
    users = {}
    for payload in DEFAULT_USERS:
        user = db.execute(select(User).where(User.username == payload["username"])).scalar_one_or_none()
        if not user:
            user = User(
                username=payload["username"],
                password_hash=hash_password(payload["password"]),
                role=payload.get("role", "student"),
                status=payload.get("status", "active"),
                phone=payload["phone"],
                avatar=payload["avatar"],
            )
            db.add(user)
            db.flush()
        else:
            user.role = payload.get("role", "student")
            user.status = payload.get("status", "active")
        users[payload["username"]] = user
    return users


def ensure_categories(db: Session):
    categories = {}
    for name in DEFAULT_CATEGORIES:
        category = db.execute(select(Category).where(Category.name == name)).scalar_one_or_none()
        if not category:
            category = Category(name=name)
            db.add(category)
            db.flush()
        categories[name] = category
    return categories


def ensure_items(db: Session, users, categories):
    existing_items = {
        item.title: item
        for item in db.execute(select(Item)).scalars().all()
    }
    user_list = list(users.values())
    now = datetime.utcnow()

    for category_name, templates in ITEM_TEMPLATES.items():
        category = categories[category_name]
        image_list = IMAGE_POOL[category_name]
        for index, template in enumerate(templates):
            title, description, price, original_price, condition_level, status = template
            image_url = image_list[index % len(image_list)]
            if title in existing_items:
                existing_item = existing_items[title]
                existing_item.image_url = image_url
                continue
            seller = user_list[index % len(user_list)]
            created_at = now - timedelta(days=index + category.id * 2)
            item = Item(
                title=title,
                description=description,
                price=price,
                original_price=original_price,
                condition_level=condition_level,
                image_url=image_url,
                status=status,
                seller_id=seller.id,
                category_id=category.id,
                created_at=created_at,
                updated_at=created_at,
            )
            db.add(item)
            existing_items[title] = item
    db.flush()


def ensure_interactions(db: Session, users):
    items = db.execute(select(Item).order_by(Item.id.asc())).scalars().all()
    user_list = list(users.values())
    existing_favorites = {
        (favorite.user_id, favorite.item_id)
        for favorite in db.execute(select(Favorite)).scalars().all()
    }
    favorite_target = 24
    favorite_count = len(existing_favorites)
    if favorite_count < favorite_target:
        for index, item in enumerate(items):
            for offset in range(1, len(user_list) + 1):
                user = user_list[(index + offset) % len(user_list)]
                key = (user.id, item.id)
                if item.seller_id == user.id or key in existing_favorites:
                    continue
                db.add(Favorite(user_id=user.id, item_id=item.id))
                existing_favorites.add(key)
                favorite_count += 1
                if favorite_count >= favorite_target:
                    break
            if favorite_count >= favorite_target:
                break

    existing_message_keys = {
        (message.item_id, message.sender_id, message.content)
        for message in db.execute(select(Message)).scalars().all()
    }
    message_target = 20
    message_count = len(existing_message_keys)
    if message_count < message_target:
        for index, item in enumerate(items):
            sender = user_list[(index + 2) % len(user_list)]
            if item.seller_id == sender.id:
                sender = user_list[(index + 3) % len(user_list)]
            content = MESSAGE_TEMPLATES[index % len(MESSAGE_TEMPLATES)]
            key = (item.id, sender.id, content)
            if key in existing_message_keys:
                continue
            db.add(
                Message(
                    item_id=item.id,
                    sender_id=sender.id,
                    content=content,
                    created_at=datetime.utcnow() - timedelta(hours=index * 3),
                )
            )
            existing_message_keys.add(key)
            message_count += 1
            if message_count >= message_target:
                break


def seed_data(db: Session) -> None:
    users = ensure_users(db)
    categories = ensure_categories(db)
    ensure_items(db, users, categories)
    ensure_interactions(db, users)
    db.commit()
