# Credits to https://python.algorithms-library.com/ciphers/rabin_miller
# Primality Testing with the Rabin-Miller Algorithm

from random import randrange


def miller_rabin(num: int) -> bool:
    s = num - 1
    t = 0

    while s % 2 == 0:
        s >>= 1
        t += 1

    for _ in range(10):
        a = randrange(2, num - 1)
        v = pow(a, s, num)
        if v == 1:
            continue
        i = 0
        while v != (num - 1):
            if i == t - 1:
                return False
            i += 1
            v = pow(v, 2, num)
    return True


def is_prime(num: int) -> bool:
    if num < 2:
        return False

    low_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
                  101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197,
                  199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313,
                  317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439,
                  443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571,
                  577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691,
                  701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829,
                  839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977,
                  983, 991, 997]

    if num in low_primes:
        return True

    for prime in low_primes:
        if (num % prime) == 0:
            return False

    return miller_rabin(num)


if __name__ == "__main__":
    import time

    list_primes = [
        22626732453295427810820712567981042493503680618896317655924105969649505399634000609024701419562046292427400009339964405065905677285374902979249938499546497464674422043085092840846138007860069455796112934317993021020998306484327480868655488651287520317167715676730950540018785190255587874754017208982869756861618935385454538774075212093198498876256859072467086014298576047867390489482073002188934580783715078679678818020210019954407962240697773067433696477514910072990254926655715777629860553435078012166068827072924456193144590698415842458423918676117971047556827109247084603059169852783186736107172321157113929013813,
        19559661230842963557209265856797013967930535733769737480980926531699291243337073534098808668700040535692848224013639726547392119414715811857854553165374052272208994472538598640582887331390550448232088263057023467358118113193282352079769633753728662889741803788581190138160277158115083433832315861206360138904381557257857191518026977333095108613953654733631281418963518231980577186972084997204661489311684964643119991974633711414315052381688705604528617949739022562368728767390821692236431985850017542986610048906647284849862660633306651067058493155433718755257829958869687440647377172084969779332228856980254206040137,
        18090788040002826735466986166621747144180564039041662167294284417381631715111373257425134918507850643858648405349162725256714725618350553432478557151869973988073956682675145237208452111257416446104321472866657406204458143429183265399938553459067564563299821107218906153408623555242664535315786673155961513689465372785991399030554970975017603339984016311936096966151188630806761333981890892646924321012415015852584666852913043939655151116423954439350351751518866587140340886169249523447422737421072819725449996643404634046447697051434726065148158102975743936149905440810019964730489776824576108614078736013917468061813,
        24177440014652567778319468862077381176784376783015354955130444631217646013745933668148594267645021999635473268477071792085428947635944375367449076607916001674438832269802254769221539404243117491368551801896049317765590529672655333941688107743894779329910526791596544322412767787325235783344035827274455390657589069348923901629473865279129666047585823636838317269079958382615327258630274589706548837715346588036559380608465561268373101539261644101896026382609786375236455455087537296795379514832859077207106806805409459206072118267053598598092599090073880243250642611125094877490219802353178375448595171895753627572797,
        28205894962002845340897540739580789316825695549114010633089973329811481314573967491085723603659765231898125739686225706398142118217194778898539258273286100003606283548952951770238482662270518240495944472608246485584724701981182615450541644186245577380726856796931410708592698406058614453508414170092374898990257490472710190535448729240939673197209602482602044354754971859980001843431217999018941002994511372183856251959703876655118363082733513519636253143032800081025846592512345738069711528380029138641743276208661347481743653714721135316999244015948380307893918753900052065048375732493702217677424703577793360795977,
        22847415976354042292247530753986535152605978105015638481972033445220982828832825471480783972276923065469971446046853729403200896757606229768820251175105912975735355822051168160328098489650276423798645199535203783932723729115967826917123465138489797537927910482643221634066876328313541560420839425782090041478630799154503081512391920707327147947715424398995810484049205711683633786314833981441895691140888534486818607537382439528081737775186048450406543774861539407215166503351649769630792526693381324035287879409029513804831358501697463684484604291825421245336975632863606345606208627592021950567232670558811779690837,
        16918843187529755258435181156454481119014462863867290793174799572162065076107688190715575304596412626093098135232084922930588642705003839743478558973814609604430588902893333153078123053519949363201543330428961792891797263047177832021747507315717334607999528143828183833734821401065505365455152032624671122056726921795189269369310941197044547746772285499281298960688823399457034154416333166153045354212870572893194280407235564757150609030486128493864060754159578319267349011754310013087539676986962480195359133930248023714690969485428061605537772459922716990252692121705300348274286669084739974762611892391932920432267,
        30636804983497225371440600747554510329318152595936283853015267574314332755883520409723473822532742470980198849131261018389314063513028600011962505986043142883499223248358087422777353001898069639005700181788087930529730240630933206359652461854063727169798451286382926124401311089347467999534205944561291551661000516377687422347419312755864034897024468914464633284936476141694814466955752917795265745705641735725450107384504391277637498633974463896872346226371864856056388153170486068148229110679745679025028105872358862303698594199826523461366603363882092154897325114446943142992203811008597451418911429636658889601417,
        22136965181060564325158492565462660405450772359820501045115950921126836314951509353529215716991904799809173265270489918277278855885434143934043361991145676780225406466592696797124757342065752256844664585044069160599277410610113889104771700929697850870379466109292435859517533181307272846144101980149550137634125722954617840363322680588287263775642946736277477432041232777339361086492265566946787619341614785344584690926890450693725846514867733011107415405776053550143735918007661049580232769771067064376263833076384046219332346641173295307247449838069868536154625523501440001135792063826345973184593287061901231456509,
        26365349380142067750824088492315581529564002496285965335750518136413128414542949481821868553301593728437125697731692503262245568240080676247864046221062189548155755429112267723666958654237658827030992675032852682937804044669281658842036558377172312039195862487579365998454805274640255578593353583319878064123661509203683140403496232165497088675702065221461258176246182430235292161480699113435515109825215230780158830883619950587057580625798264247198590353564164229576534768849577294744200707161116535292844565731349650341601173083797548441327293744004313705145428180296210271677269409943604391659006665175943578736789,
        21733544628543058633453269561282178297127772815787263173962762889269751210423853765061897830356982712013938447380901282728393288822889782567645223332747240466667069322851457351341627861598944727078376245038502168570504632296623575633919441344911508206610721309864890208143970057463288069614606331950202549226887148793037973309178742855952867317346027848734873255982638978042279109211326721605737659619525776128200730852414038308521938320877752745344604460219727418252053093195245424676775218628561708605410454073750045677067748868580098835459945483098522551530715610886597344273885579530368234275553638267989323452879,
        28029708372218041540741224992519535504224911079014595076682018652017670547731178097845484145712848275720938759543204076912868672778326770829093557034760849375214382377495389538958206786543904493384834090968874628063232303470003695060784512035947817124046369728426659178700074806164472989800093370273196523338170206522614723737600011521092195062552483423331317530331225671753314649728618451641839796257449417189438403869121785526237580380904900256756216927471960486689841060890559198334161027905557048394936051839257303187138194150506753976147479362854124770321274682579807419741098563714956496534771485788109731166589,
        30835723097023805250591243816471994316309686616680863364994385391324744290531857371145344844889060156595343815976612479576714540042855162317837600655594705852202631564232962421002587273295596245989122438708834511167679489694584798101461558588573776126495848352660452471869458576137775925543847224279246022972125194325312795674420425050129962617607217167464336711232008550588126266967511236490332844025626729646231749498512464838972911281849490466445574874156143465890574740867177000525707633877544168990700236671857493586764476292417647661340210669216801945694682406174662802244338872621015843055189325224987209747331,
        20053723787124012424841386699084965517341396925083594952294973156556642755060565312655641812168926413727128817867149969537035344053308533669317553536900060204356058918058362307643962196038794126808319982363266540584976161202536517339830298070299138673522165994954563865468767719091920707322078583657228174189084593860277359028400615306024249530175267325382032612661068279462748599533729579858176588584097702944129151393900168591384784730318656304768352809807173407535156863486917457356216784323616245593300778345480702053175130523352044404047437715148701576450894335284984679791173611202876529146731538763890011478373,
        17178161541156138155890111361515243520112442222198767375872832954725007172397916370381987094707342613260026794433195398818750847154106679190566064967414317038413957290431696623891641517194868960528351993844015063844481374141221765366388925586978388966492485192743404754468271998700497323787623759267142816116626057445794062241642648277034533074789662688139500356948350278700649362953557042635144730176773578257875888791463293530854026332753385981808353539954729088195341119666242800539109996839614041112536028149837012328912424418195186537890548866207029368030203135202363945228589263286022235364524164291896999793463,
        28326367340528286626492726127222320825838938372533936577846655332557229675017995728439501717840729154437937619420546412710709405054054467626256763266787263004028955923239340272082824433995102427901215189121853882417144722193127143083818295978834509683852135977040375779515407374112736479065161260432807121442894462827417507602343673826881341386068281967513470167572430255545869402935095144527753444341483925341973358763759584919203714931747912042086138293037549879481649421097349252098146734823479546077834059505864596548748788047240872303214659759866394693122555237168678102617596279879866561710656554416837566154091,
        16241372085073675918636995060507296740649074842870048825324103517024946270850323211759756002456480307115905691807098320206950680429809613875508262508335187379120451086814751441369453327133531976177628587853427091363434710327904047289585290282826370088189946688061947652266495949194744382678676910939384506119100597774512388697937874709046685477874213520941879179354419192998378891428624706048885661958054011116750846631049126978425131265049864401651141342027740168074702729937598558782139608766906945638456312198252439842304034322519451486625819666568477349384784783017818435473588036818834679060730733708086342858717,
        20449971668003868288829598112394278866789303225227282748935031411295725194996580746205617528180765426310214997262798065841583238318793965975454351354165069952478037874402206967397009802711443047195495401189229456547665790485390585439492343442296878881744232688805906296484031327988397409073870042385441914251064191601081042096170458764321918786027000095493862513800894082642242825129494224996390930235934846506548994960140427327500268919905888903522920230510851305878350773132696684015763794721612083781305681477589517212103926965269462476440096913561100336389905181066350799612979457914166123781016919610012679647733,
        23272858343625698482089705611215594250477306393070143624905744432898497410711108445007661622208410918946473693301487581096196780189868534785592983246473154533955711800165843049834832088619376878737960765246213174172069809804876515415943742127603395414559822633948499333353470273340726848750916449513824671313031539240385889728468926701559875386983494923436305497693654843276445413344278044417075061714489385097590100717339549935758060973723786820767881350393195931947956555554983983315341483109251589797945454680508585176903845864479486087894971297341001743265284197391996278973102282227688749009378495568462435703243,
        19427699810141903892322598710074904038247761302342896480663329026414867019164491505905717880323243183128404149855456099401807456636769747219505867762650657042158984701058112053762916223261579457763994984012569971398040815217669867397475931892606430880976518570870885355935673888780425380434640818918522525918395057374039663731967860213188513458865927111028040613073498927910367614674177332672444459626419202112478583965728136272969948711910386037828885332437165119241416542214512839616682487433292076597657697991075222467010679366897194023491317854865479578889181847999979236595565527887466944022148612139352788177203]

    start = time.time()
    print(is_prime(list_primes[0]))
    print(time.time() - start)
