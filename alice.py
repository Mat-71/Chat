from key_generator import get_key_from_password
from Client import Client

username = "alice"
password = "canada"
# public, private = get_key_from_password(username + password)
public = 690852070184464435882542383267108001959431594348489408062917839835697052704919807108991157216534449910674545227999943061020456195457985006352083477828318315952953278220956935081808987842627988741009176062752188536252842658673116560301035939536823787484446121429497236725451562755915450654577953111527053942074572664328377380979480651758563875633281881615227565337657969216873584172121156956073735115052923515800918052147970342460972669469704582124698380661520795148973834045924722464439998392136591419832727185938163066680050250317099932662174219278324766445621600019861660366089431815170031785786868529202705298003126995247603344453552018176302471008617930137634772945396836042912888538846117785108254597187490887039201862711851083021480193599747129492966840857257447854157535156267195131621785132881668899197815574974841402495469853362169358391961028883973176443363336221514212675155566910875435750480871362782899963336069399587323123994813947459340340840889186051825870277557460538572938723826914781683961288521838738335497000022603711158546966770204766885270209806320440342268761097371231038622139858337496866745005994598807339814363945021159256760156090722780059432771872675372747468483173437386855454553028406115370630140861611
private = (public,
           198526283439645066465903546150562964446068254823460045806932445452579193334936825415927345833025516809859067553884415332837912195081560517335685004469852432127530541354277460951763258434780550100850295448217220298506947003841964145141666689798083561800121668750197925740427991537332433315190908814095686511300340677591228332331149718701939873198370350740186165646949242935462108590774032210106301073009013359981059396617219669187901464579137683982398410104191847888072756100933828191293444767369706062372549111078832186929297745765322535847333980372441373979132270216428195518173890617133790204338375192799098965123394212478445978463997930941022988302929360539648059452206091101188157014622642320706007011020029468381149857832223169277380800762746103234109509227117223449637575277589707736544734792341266735378516253137876060986430871752681827295411217525161566564000437180140739473776239842278593233950833026456581513967017219918632343036596473397749205243061718747469144971408127048455773626706981490849426742291633322086297174444289950911522133240137379020078911485053943537830752733597332098031037324331174101355806681855025893161663647697810631814176329003526549047249686135822495862606797240557516285581164268734818805174486673)
alice = Client(username, public, private)
alice.get_messages()
