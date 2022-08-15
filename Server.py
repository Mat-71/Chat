import socket
import json
import time
import select
from key_generator import get_key_from_password, random_number
import rsa
import aes
from User import User
from conversion import to_bytes, from_bytes


# TODO: timeout for socket

class Server:
    def __init__(self, ip: str, port: int, password: str, key_size: int = 4096):
        self.IP = ip
        self.PORT = port
        self.HEADER_LENGTH = 10
        self.AES_LENGTH = 80
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.IP, self.PORT))
        self.server_socket.listen()
        self.sockets_list = [self.server_socket]
        self.users: dict[str, User] = {}
        self.clients = {}
        """example: self.users = {"username": User(username="username", pub_key=pub_key)} self.clients = {socket: {
        "username": username, "aes_key": aes_key, "check": check, "public_key": public_key, "auth": auth}} """
        # self.public_key, self.private_key = get_key_from_password(password, key_size)
        self.public_key = 1026279905880425632307278951186601703616021181669355052888001644929551758317221892591621435650373422157915375620420627710485919235212629272612984633220889258478711802253699429216727982502352187333063234026813566127109336160978233960590632051587818493109056738991302343859435557744611878416968679068083384484520471596792218848775001222438043096103333053415504823605397753246089640819685641330525791999829384583094453777462066077026738533332579558110370358442658692900529319129618038304113291204099556839147776744574804005164150904962800716296273156117984183121893595682311940321552768661236972349400094172835350027234640910371571627168932003291635746260170818793790402436223484821742160675498620537693002688688404210235697541222042263848126070473570600347894747033732587209702388636258683609935218605460517574304987714407067519610903321490842565687391649759477190898306482162375399220460978646715395853060286527236933408101164438175909340451685242275645304011775925069840662027333588401170646441556443535047293197084755625685636789693853429576545177899586450386651596415508311594963510137146544978430716161434500659933066954055972170065240153361177352296822890175693274848739540862674216539916413484581451729535813344294971837647283112552960151676195680752714980058621677230768996623930123865777220179260894659714197107480839750206956383147096673670831077939267401747477513913416363166379869923489467033005369606533253268295253808150124572952976287960572171801674708521653756790344189041127532433881570372228932615028785958266511026454718055851873889257106056990976350993286772668554237222016356502703238588697287956759810779069455785195281200392981101601203320535960052408639039737642443076949283153824290380895042710147990499883064385297592020716398373786110102102387002339533192627702987094937000613618033469628293964927772412079385504925905585445370458810223559026720326174992716662637536319213165628409711891441721551339769628784690159348863362019936916322506762482814336829960114259264681441110400852825649285564662070972301731720130230362113461808903562193702957330801285854562257337200423319762335750187939022363530490906178097037388063055508360024050291969988739908906623481128298112799121157956031526395349493381588327845134914938059703265252746929076638619699833258025775714327426883523404759728949826337542601977338611687474737178471948894138002291281287391717717340427221793414294193460753701227819598617085159289135805757436524777937007806089973302558217
        self.private_key = (self.public_key,
                            366182909182719272866829592360765586422281143661690320837588392282720269717715439162037866415129348364140762370995253953980236132203367912946610810126146671655190148830439407553045869399499573501935557997512983968084055064899446464355270151125769376731650560516542014569007447431222121319291325378458914243649033489775077369421161001960590197282151153105393362454622900985802831391847796464180769948639857318630402782125714529886831161991684703096768244836094585879518098151074785353363522918605734731932062978090806977077963665740728625812473129417930972399138804666603329607384987753091617886359946322498463845413351893558277475772743732013543651533451858136228310276159268338062753638949902233141785172838086028535812614308501095531143934448540136389141565293449544826764738329039673124108902633170403633940336492572056500581066622972395174573660166592544892686055186824007603878286456881987164756213463236841912977631530726495040420176727767602631945145663796509348216135117088532782617397643405642973372356388451188657291769385249074526113988128903208200580754849630687372577730458321784759382087473015004706225107002969999438863627809423650322811677471716258167738268846964810319049840630680736876378892312117475527128973618997765245929817714191105926000880989044113726955175944344799316820896315073540041793098486104152654360621088294834332102690903754721496293122036835788638546893399922106846674393060945598846870991665055829256252340596624622558043708736402789204047693279250905312236985547950855527936593349130691986672954066400495975358493580439961616554782884468289954109048720152178357482643689384431732844923484772748987809380009974453778667844378154072587423001935170704423802455326331666705214680326044093094164385019737934828753927619932041907074075090356052280956691060745416784250462982368380619513639549987885996922348435617063566233477355505831553838400180507225916047725619669177287023148891551593344398943140125035584775506931173076511953853688551312997009554468325237598670369212983176808611365286983772714273708427699402954294003339195654802524303815799250253453690455924674785021778450417279129762610965517460893989184108077389530577811971523421522283008710931664045906874244848648793753818794248414333833057034682081107940200182830638081784480990397919427122918563229957074490966379368054629941524409982858829878614821090422349395876574461346151625646835423654952960965343204289147296362487600549824594543870671959175707382000061889093345)
        self.file_number = 0
        self.load()

    def load(self):
        users = None
        for user in range(3):
            try:
                with open(f"user{user}.json") as jsonFile:
                    users_2 = json.load(jsonFile)
                    jsonFile.close()
                if users is None:
                    users = users_2
                else:
                    if users[0] < users_2[0]:
                        users = users_2
                        self.file_number = (user + 1) % 3
            except IOError:
                pass
        self.users = {}
        if users is not None:
            users = users[1]
            for user in users:
                self.users[user['username']] = User(**user)

    def save(self):
        file_name = f"user{str(self.file_number)}.json"
        self.file_number = (self.file_number + 1) % 3
        with open(file_name, 'w') as outfile:
            outfile.write(json.dumps([int(time.time() * 1000), [u.__dict__() for u in self.users.values()]], indent=2))

    def receive(self, client: socket.socket, target_type: type = str):
        try:
            message_header = client.recv(self.HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = from_bytes(message_header, int)
            message = b''
            while message_length > 0:
                new_part = client.recv(message_length)
                message_length -= len(new_part)
                message += new_part
            return from_bytes(message, target_type)
        except Exception as e:
            print("Exception (receive):", e)
            return False

    def header(self, data: bytes) -> bytes:
        message_header = to_bytes(len(data))
        return b'\x00' * (self.HEADER_LENGTH - len(message_header)) + message_header

    def send(self, data, client: socket.socket):
        data = to_bytes(data)
        client.send(self.header(data) + data)

    def send_aes(self, data, aes_key: bytes, client: socket.socket):
        print("sent:", data)
        self.send(aes.encrypt(str(data), aes_key), client)

    def send_success(self, client: socket.socket, key: bytes):
        self.send_aes(0, key, client)

    def send_fail(self, client: socket.socket, key: bytes, error_code: int = -1):
        self.send_aes(error_code, key, client)

    def send_public_key(self, client: socket.socket):
        self.send(self.public_key, client)

    def aes_protocol(self, client: socket.socket, data: str):
        # data = "RAND_NUM|PUB_KEY"
        print("received:", data)
        c_rand_num, c_pub_key = data.split("|", 1)
        c_rand_num = rsa.crypt(int(c_rand_num), self.private_key)
        c_pub_key = rsa.crypt(int(c_pub_key), self.private_key)
        s_rand_num = random_number(self.AES_LENGTH)
        aes_key = to_bytes(c_rand_num) + to_bytes(s_rand_num)
        self.clients[client] = {"aes_key": aes_key, "auth": False}
        self.send(rsa.crypt(s_rand_num, c_pub_key), client)

    def login(self, client_data: dict, aes_key: bytes, client: socket.socket, username: str):
        # data = "USERNAME"
        if username not in self.users:
            return self.send_fail(client, aes_key)
        _check = random_number(256)
        client_data['check'] = _check
        client_data['username'] = username
        client_data["auth"] = False
        key = self.users[username].pub_key
        self.send_aes(rsa.crypt(_check, key), aes_key, client)

    def check_login(self, client_data: dict, client: socket.socket, aes_key: bytes, check: int):
        # data = "CHECK"
        if "check" not in client_data or "username" not in client_data:
            return
        if client_data["check"] != check:
            return self.send_fail(client, aes_key, 1)
        self.send_success(client, aes_key)
        print('Accepted new connection from {}'.format(client_data["username"]))
        client_data["auth"] = True

    def sign_up(self, client_data: dict, aes_key: bytes, client: socket.socket, data: str):
        # data = "sign up|USER_PUB_KEY|USERNAME"
        user_pub_key, username = data.split("|", 1)
        user_pub_key = int(user_pub_key)
        if username in self.users:
            return self.send_fail(client, aes_key, 1)
        if user_pub_key <= 0 or len(username) < 3:
            return self.send_fail(client, aes_key, 2)
        client_data['username'] = username
        client_data['auth'] = True
        self.users[username] = User(username, user_pub_key)
        print('Accepted new connection from {}'.format(username))
        self.send_success(client, aes_key)

    def request_friend(self, aes_key: bytes, client: socket.socket, user: User, data: str):
        friend_name, key_user, key_friend = data.rsplit("|", 2)
        if friend_name not in self.users or friend_name == user.username or friend_name in user.keys:
            return self.send_fail(client, aes_key, 1)
        self.users[friend_name].add_request(user.username, key_friend)
        user.add_pending(friend_name, key_user)
        self.send_success(client, aes_key)

    def accept_friend(self, aes_key: bytes, client: socket.socket, user: User, data: str):
        friend_name, key_user, key_friend = data.rsplit("|", 2)
        if friend_name not in user.get_requests():
            return self.send_fail(client, aes_key, 1)
        user.add_friend(friend_name, key_user)
        self.users[friend_name].add_friend(user.username, key_friend)
        self.send_success(client, aes_key)

    def get_pub_key(self, client: socket.socket, aes_key: bytes, friend_name: str):
        if friend_name not in self.users:
            return self.send_fail(client, aes_key, 1)
        self.send_aes(self.users[friend_name].pub_key, aes_key, client)

    def get_aes_key(self, client: socket.socket, aes_key: bytes, user: User, friend_name: str):
        if friend_name not in user.keys:
            return self.send_fail(client, aes_key, 1)
        self.send_aes(user.get_aes_key(friend_name), aes_key, client)

    def message_reception(self, client: socket.socket, aes_key: bytes, user: User, data: str):
        # data = "USERNAME_LENGTH|USERNAME|CONTENT"
        username_length, data = data.split("|", 1)
        friend, content = data[:int(username_length)], data[int(username_length) + 1:]
        if friend not in user.keys:
            return self.send_fail(client, aes_key, 1)
        sent_time = self.users[friend].new_message(content, user.username)
        self.send_aes(sent_time, aes_key, client)

    def aes_data_receive(self, client: socket.socket, data: str):
        client_data = self.clients[client]
        aes_key = client_data["aes_key"]
        data = aes.decrypt(to_bytes(data), aes_key)
        print("received:", data)
        action = data.split("|", 1)[0]
        data = data.removeprefix(action).removeprefix('|')
        match action:
            case 'login':
                return self.login(client_data, aes_key, client, data)
            case 'check':
                return self.check_login(client_data, client, aes_key, int(data))
            case 'sign up':
                # TODO: check if user password is strong enough (shhhhhhhh!!!!)
                return self.sign_up(client_data, aes_key, client, data)
        if "username" not in client_data or not client_data["auth"]:
            return self.send_fail(client, aes_key)
        user = self.users[client_data["username"]]
        match action:
            case 'get friends':
                return self.send_aes(user.get_friends(), aes_key, client)
            case 'request friend':
                return self.request_friend(aes_key, client, user, data)
            case 'get requests':
                return self.send_aes(user.get_requests(), aes_key, client)
            case 'accept friend':
                return self.accept_friend(aes_key, client, user, data)
            case 'get pending':
                return self.send_aes(user.get_pending(), aes_key, client)
            case 'get pub key':
                return self.get_pub_key(client, aes_key, data)
            case 'get aes key':
                return self.get_aes_key(client, aes_key, user, data)
            case 'send message':
                return self.message_reception(client, aes_key, user, data)
            case "get messages":
                return self.send_aes(user.get_messages(), aes_key, client)
            case _:
                return self.send_fail(client, aes_key)

    def listen_client(self, client: socket.socket, data: str):
        if not data:
            return self.sockets_list.remove(client)
        if data == 'key':  # send key to client
            return self.send_public_key(client)
        if data.startswith("aes"):  # server send aes key to client
            print("received aes key:", data)
            return self.aes_protocol(client, data.removeprefix("aes").removeprefix('|'))
        if client in self.clients:  # connection is secure
            self.aes_data_receive(client, data)
        else:
            self.send("-1", client)

    def listen(self):
        read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)
        for notified_socket in read_sockets:
            if notified_socket == self.server_socket:
                self.sockets_list.append(self.server_socket.accept()[0])
            else:
                self.listen_client(notified_socket, self.receive(notified_socket))
        for notified_socket in exception_sockets:
            self.sockets_list.remove(notified_socket)
            print("Socket {} is offline".format(notified_socket))
            if notified_socket in self.clients:
                del self.clients[notified_socket]


if __name__ == "__main__":
    server = Server("", 404, "5")
    print(f'Listening for connections on {server.IP}: {server.PORT}...')
    while True:
        server.listen()
        server.save()
