/*
 * 闂佹彃绻愰悺娆撳捶閸濆嫮鏉介柣婊呭閺嬪啯绂?
 * 閻庡湱鍋熼獮鍥煂韫囨挾鎽嶉柛锕€鎼鐑藉礂閸撲焦绁查柛蹇氭珪閹奸攱鎷?
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "quantum_field.h"
#include "quantum_state.h"

// 闁告帗绻傞～鎰版嚍閸屾粌浠悗鐟扮秺閸?
#define INITIAL_NODE_CAPACITY 16
#define MAX_DIMENSIONS 4  // 闁衡偓椤栨稑鐦柡鍫氬亾濠?濞戞搩浜炲ǎ顔芥償閿旇偐绀剎,y,z,t闁?

/**
 * 闁告帗绋戠紓鎾寸▔閳ь剚绋夐鍛厐闁汇劌瀚伴崳铏光偓娑欏姇濠р偓
 * @param name 闁革箑鎼幃鏇犵矓?
 * @param type 闁革箒娅ｇ悮顐﹀垂?
 * @return 闁哄倹婢橀崹鍗烆嚈閾忚鐣遍梺鎻掔箰閻℃瑩宕烽悜妯虹樄闂?
 */
QField* quantum_field_create(const char* name, QFieldType type) {
    QField* field = (QField*)malloc(sizeof(QField));
    if (!field) {
        fprintf(stderr, "闂佹寧鐟ㄩ銈夋晬濮橆厽锟ユ繛澶嬫礀閸ㄥ酣鏌婂澶婃閻庢稒鍔曞┃鈧柛鎰噹閻♀晿n");
        return NULL;
    }
    
    // 闁告帗绻傞～鎰板礌閺嵮勭皻閻忕偟鍋為埀?
    strncpy(field->name, name, sizeof(field->name) - 1);
    field->name[sizeof(field->name) - 1] = '\0';
    field->type = type;
    field->intensity = 1.0; // 濮掓稒顭堥璇差嚕閸濆嫬顔?
    field->dimension = 3;   // 濮掓稒顭堥缁樼▔?缂備礁顕埞鏍⒒?
    field->node_count = 0;
    field->max_nodes = INITIAL_NODE_CAPACITY;
    field->private_data = NULL;
    
    // 闁告帒妫濋崢銈夋嚍閸屾粌浠柡浣瑰缁?
    field->nodes = (QFieldNode*)malloc(field->max_nodes * sizeof(QFieldNode));
    if (!field->nodes) {
        fprintf(stderr, "闂佹寧鐟ㄩ銈夋晬濮橆厽锟ユ繛澶嬫礀閸ㄥ酣鏌婂鍛皻闁煎搫鍊婚崑锝夊极閹殿喚鐭嬮柛鎰噹閻♀晿n");
        free(field);
        return NULL;
    }
    
    return field;
}

/**
 * 闂佸簱鍋撴慨锝勭窔閸ｈ櫣鈧稒鍔曞┃鈧鐐茬埣閸ｆ挳寮ㄩ幑鎰偒婵?
 * @param field 閻熸洑绶氶弨銏犘掓担鐑樼暠闂佹彃绻愰悺娆撳捶?
 */
void quantum_field_destroy(QField* field) {
    if (!field) return;
    
    // 闂佹彃锕ラ弬渚€鎳為崒婊冧化闁轰焦澹嗙划?
    if (field->nodes) {
        // 闂佹彃锕ラ弬浣感掕箛搴ㄥ殝闁煎搫鍊婚崑锝夊矗椤栨繂鍘撮柟闀愮劍濠€渚€鎯冮崟顓炐﹂柟?
        for (int i = 0; i < field->node_count; i++) {
            if (field->nodes[i].state) {
                // 婵炲鍔嶉崜浼存晬濮樺磭绠归梺鎻掕嫰瑜把囧及椤栨簽鈺呮⒔閵堝牆螡闁绘劗鎳撻顕€鎮╅懜纰樺亾娴ｇ儤鐣辩€殿喗娲滈弫銈夋晬鐏炶偐鐟濋梺搴撳亾婵絼鑳舵慨鎼佸箑娴ｅ壊鍤犻悹?
                // 闁绘鍩栭埀顑跨椤曨喚鎸掗敍鍕暠闁汇垻鍠庨幊锟犲川閵婏附鍩傞柣銏犲船閸ㄥ崬顕欓崫鍕殜闁汇劌瀚崬顒勬儘娴ｄ警鍚€闁?
                field->nodes[i].state = NULL;
            }
        }
        free(field->nodes);
    }
    
    // 闂佹彃锕ラ弬浣虹矓娴ｈ绠掗柡浣哄瀹?
    if (field->private_data) {
        free(field->private_data);
    }
    
    // 闂佹彃锕ラ弬渚€宕烽崫鍕靛殸閻犵偐鍓濆﹢浼寸叕?
    free(field);
}

/**
 * 闁告碍鍨块崳铏光偓娑欏姇濠р偓婵烇綀顕ф慨鐐烘嚍閸屾粌浠?
 * @param field 闁烩晩鍠楅悥锝夋煂韫囨挾鎽嶉柛?
 * @param node 閻熸洑鐒﹂崸濠囧礉閻樺灚鐣遍柤鍝勫€婚崑?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€0闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛銉у仱閺佸﹦鎷犻婊呭灣
 */
int quantum_field_add_node(QField* field, QFieldNode* node) {
    if (!field || !node) {
        return -1; // 闁告瑥鍊归弳鐔兼煥濞嗘帩鍤?
    }
    
    // 婵☆偀鍋撻柡灞诲劜濡叉悂宕ラ敃鍌涗粯閻熸洑鐒︽晶璺ㄤ沪閺団€澄濋柣鎰潐閺嗙喓绱?
    if (field->node_count >= field->max_nodes) {
        int new_capacity = field->max_nodes * 2;
        QFieldNode* new_nodes = (QFieldNode*)realloc(field->nodes, new_capacity * sizeof(QFieldNode));
        
        if (!new_nodes) {
            fprintf(stderr, "闂佹寧鐟ㄩ銈夋晬濮橆厽锟ユ繛澶嬫礃婢ц法浠﹂弴鐐寸皻闁煎搫鍊婚崑锝夊极閹殿喚鐭媆n");
            return -2; // 闁告劕鎳庨悺銊╁礆閸℃稑甯冲鎯扮簿鐟?
        }
        
        field->nodes = new_nodes;
        field->max_nodes = new_capacity;
    }
    
    // 婵烇綀顕ф慨鐐哄棘閹峰苯螡闁?
    field->nodes[field->node_count] = *node;
    field->node_count++;
    
    return 0; // 闁瑰瓨鍔曟慨?
}

/**
 * 闁告碍鍨块崳铏光偓娑欏姇濠р偓婵烇綀顕ф慨鐐哄捶閾忕懓浠?
 * @param field 闁烩晩鍠楅悥锝夋煂韫囨挾鎽嶉柛?
 * @param position 闁绘劕婀卞▓鎴炴媴瀹ュ洨鏋傞柡浣瑰缁?
 * @param intensity 闁绘劕婀卞▓鎴濐嚕閸濆嫬顔?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€0闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛銉у仱閺佸﹦鎷犻婊呭灣
 */
int quantum_field_add_point(QField* field, double* position, double intensity) {
    if (!field || !position) {
        return -1; // 闁告瑥鍊归弳鐔兼煥濞嗘帩鍤?
    }
    
    // 闁告帗绋戠紓鎾诲棘閹峰苯螡闁?
    QFieldNode node;
    node.position = (double*)malloc(field->dimension * sizeof(double));
    if (!node.position) {
        fprintf(stderr, "闂佹寧鐟ㄩ銈夋晬濮橆厽锟ユ繛澶嬫磻鐠愮喖宕烽搹鐟颁化濞达絽绉堕悿鍡涘礆閸℃稑甯抽柛鎰噹閻♀晿n");
        return -2;
    }
    
    // 濠㈣泛绉撮崺妤佹媴瀹ュ洨鏋傞柡浣哄瀹?
    memcpy(node.position, position, field->dimension * sizeof(double));
    
    // 閻犱礁澧介悿鍡涙嚍閸屾粌浠柛褎鍔栭悥锝夋儍閸曨偄鎮戦悗纭咁潐閳ь儸鍐憻婵炲牏顣槐娆撴偨閵娿倗鑹鹃柡鍐勫懎顣煎ù鐙呯悼閻栨粓鏁?
    if (field->dimension >= 3) {
        node.x = position[0];
        node.y = position[1];
        node.z = position[2];
    } else if (field->dimension == 2) {
        node.x = position[0];
        node.y = position[1];
        node.z = 0.0;
    } else if (field->dimension == 1) {
        node.x = position[0];
        node.y = 0.0;
        node.z = 0.0;
    }
    
    node.intensity = intensity;
    node.state = NULL;
    
    // 婵烇綀顕ф慨鐐烘嚍閸屾粌浠柛鎺撴緲濠р偓
    int result = quantum_field_add_node(field, &node);
    
    // 闂佹彃锕ラ弬浣圭▔鐎涙ɑ顦ч柛鎺戞閸樸倝鎯冮崟顐㈡暥閻?
    free(node.position);
    
    return result;
}

/**
 * 閻犱緤绱曢悾缁樼▔閵堝洤浠☉鏂款儔濡潡鎯冮崟顒夊剬闁告垹濞€閸ｅ嘲顕ュΔ鍕崺缂?
 * @param x1 缂佹鍏涚粩瀛樼▔椤忓棗浠柣銊ュⅰ闁秆勫姈閻?
 * @param y1 缂佹鍏涚粩瀛樼▔椤忓棗浠柣銊ュⅱ闁秆勫姈閻?
 * @param z1 缂佹鍏涚粩瀛樼▔椤忓棗浠柣銊ュⅴ闁秆勫姈閻?
 * @param x2 缂佹鍏涚花鈺傜▔椤忓棗浠柣銊ュⅰ闁秆勫姈閻?
 * @param y2 缂佹鍏涚花鈺傜▔椤忓棗浠柣銊ュⅱ闁秆勫姈閻?
 * @param z2 缂佹鍏涚花鈺傜▔椤忓棗浠柣銊ュⅴ闁秆勫姈閻?
 * @return 濞戞挶鍊楅崑锝嗙▕鐎ｎ喗锛熼柣銊ュ缁愭稓绮?
 */
static double calculate_distance(double x1, double y1, double z1, double x2, double y2, double z2) {
    double dx = x2 - x1;
    double dy = y2 - y1;
    double dz = z2 - z1;
    return sqrt(dx*dx + dy*dy + dz*dz);
}

/**
 * 闁兼儳鍢茶ぐ鍥箰閸パ呮毎濞达絽绉堕悿鍡涙儍閸曨偅绨氱€殿喖鎼€?
 * @param field 闂佹彃绻愰悺娆撳捶?
 * @param x x闁秆勫姈閻?
 * @param y y闁秆勫姈閻?
 * @param z z闁秆勫姈閻?
 * @return 閻犲洢鍎扮紞鍛磾椤旂偓鐣遍柛锕€鎼杈ㄦ償?
 */
double quantum_field_get_intensity_at(QField* field, double x, double y, double z) {
    if (!field || field->node_count == 0) {
        return 0.0; // 闁哄啰濮村┃鈧柟瀛樼墱閳规牠宕?
    }
    
    // 闁哄被鍎叉竟妯兼崉濠靛牜鐎插ù锝呯Ф閻ゅ棝寮甸埀顒佹交閹寸姵鐣遍柛锕傜細婵☆參鎮?
    double min_distance = INFINITY;
    int nearest_node_index = -1;
    
    for (int i = 0; i < field->node_count; i++) {
        double distance = calculate_distance(
            field->nodes[i].x, field->nodes[i].y, field->nodes[i].z,
            x, y, z
        );
        
        if (distance < min_distance) {
            min_distance = distance;
            nearest_node_index = i;
        }
    }
    
    // 濠碘€冲€归悘澶愬箥閹冪厒闁哄牃鍋撻弶鈺傚灱婵☆參鎮欓惂鍝ョ闁哄秷顫夊畵浣烘崉濠靛牜鐎查悹渚婄磿閻ｈ顕ｉ崫鍕唺
    if (nearest_node_index >= 0) {
        // 濞达絽绉堕悿鍡樼▔鎼淬倕螡闁绘劗鎳撻悾顒勫礂閵娾晛娅㈤柛?
        if (min_distance < 0.0001) {
            return field->nodes[nearest_node_index].intensity;
        }
        
        // 闁哄秷顫夊畵浣烘崉濠靛牜鐎查悶娑欐緲閸ｆ椽鏁嶇仦鐓庘枏闁活潿鍔屽浠嬬嵁閾忣偅鐓欑€?
        double intensity = field->nodes[nearest_node_index].intensity / (1.0 + min_distance * min_distance);
        return intensity * field->intensity;
    }
    
    return 0.0; // 闁哄牜浜濇竟姗€宕氶幏灞轿濋柣?
}

/**
 * 閻忓繐妫濋崳铏光偓娑欏姉婵悂骞€娴ｈ鏉圭紓鍐惧枛濠€顏堝捶鏉炴媽鍘柣銊ュ鐎垫氨鈧鐭紞鍛磾?
 * @param field 闂佹彃绻愰悺娆撳捶?
 * @param state 闂佹彃绻愰悺娆撴偐閼哥鍋?
 * @param x x闁秆勫姈閻?
 * @param y y闁秆勫姈閻?
 * @param z z闁秆勫姈閻?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€0闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛銉у仱閺佸﹦鎷犻婊呭灣
 */
int quantum_field_place_state(QField* field, QState* state, double x, double y, double z) {
    if (!field || !state) {
        return -1; // 闁告瑥鍊归弳鐔兼煥濞嗘帩鍤?
    }
    
    // 闁告帗绋戠紓鎾诲棘閹峰苯螡闁?
    QFieldNode node;
    node.x = x;
    node.y = y;
    node.z = z;
    node.intensity = 1.0; // 濮掓稒顭堥濠氭嚍閸屾粌浠€殿喖鎼€?
    node.state = state;
    
    // 婵烇綀顕ф慨鐐烘嚍閸屾粌浠柛鎺撴緲濠р偓
    return quantum_field_add_node(field, &node);
}

/**
 * 濞达絽娼￠崳铏光偓娑欏姇濠р偓鐟滄澘宕幖鐑芥煂韫囨挾鎽嶉柣妯垮煐閳?
 * @param field 闂佹彃绻愰悺娆撳捶?
 * @param state 闂佹彃绻愰悺娆撴偐閼哥鍋?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€0闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛銉у仱閺佸﹦鎷犻婊呭灣
 */
int quantum_field_influence_state(QField* field, QState* state) {
    if (!field || !state) {
        return -1; // 闁告瑥鍊归弳鐔兼煥濞嗘帩鍤?
    }
    
    // 閻庣數绮竟姗€宕犻崨顓熷創婵縿鍊楁慨鎼佸箑娴ｇ儤鐣遍柤鍝勫€婚崑?
    int node_index = -1;
    for (int i = 0; i < field->node_count; i++) {
        if (field->nodes[i].state == state) {
            node_index = i;
            break;
        }
    }
    
    if (node_index == -1) {
        // 闁绘鍩栭埀顑挎缁楀宕烽妸銉︾皻濞?
        return -2;
    }
    
    // 闁兼儳鍢茶ぐ鍥嚍閸屾粌浠ù锝呯Ф閻ゅ棙寰勯崟顓熺暠闁革箑鎼杈ㄦ償?
    double field_intensity = field->nodes[node_index].intensity * field->intensity;
    
    // 闁哄秷顫夊畵渚€宕烽搹纭咁潶闁搞劌顑呴幏鏉款嚕閸濆嫬顔婄憸鏉垮船閹肩兘鏌岃箛鎾舵憤闁?
    // 閺夆晜鐟╅崳鐑芥煂閸モ晜鏆忓☉鎾亾濞戞搩浜為悾婵嬪础閺囩姵鐣辨俊顖椻偓宕団偓鐑芥晬濮橆剦鏉荤€殿喛妗ㄧ粭宀勫捶閾忕顫﹂柛銊ヮ儏鐏忣噣鏌婂鍥ㄧ暠闁瑰壊鍨扮粻娆撴晬鐏炶棄娅ょ€殿喖宕崣鐐閺嶃劌鐩佹?
    // 闁兼儳鍢茶ぐ鍥偐閼哥鍋撴担楦款潶闁?
    const char* state_type = quantum_state_get_property(state, "state_type");
    int match_field_type = 0;
    
    if (state_type) {
        // 婵☆偀鍋撻柡灞诲劤婵悂骞€娴ｉ缚顫﹂柛銊ヮ儐濡叉悂宕ラ敂璺ㄧ憿闁革箒娅ｇ悮顐﹀垂鐎ｎ亜鐖遍梺?
        switch (field->type) {
            case FIELD_TYPE_COGNITIVE:
                match_field_type = (strcmp(state_type, "cognitive") == 0 || 
                                   strcmp(state_type, "consciousness") == 0 || 
                                   strcmp(state_type, "thought") == 0);
                break;
            case FIELD_TYPE_EMOTIONAL:
                match_field_type = (strcmp(state_type, "emotional") == 0 || 
                                   strcmp(state_type, "feeling") == 0);
                break;
            case FIELD_TYPE_DYNAMIC:
                match_field_type = (strcmp(state_type, "dynamic") == 0 || 
                                   strcmp(state_type, "action") == 0);
                break;
            case FIELD_TYPE_PROBABILISTIC:
                match_field_type = (strcmp(state_type, "probabilistic") == 0 || 
                                   strcmp(state_type, "form") == 0);
                break;
            case FIELD_TYPE_STRUCTURAL:
                match_field_type = (strcmp(state_type, "structural") == 0 || 
                                   strcmp(state_type, "structure") == 0);
                break;
            default:
                break;
        }
    }
    
    // 閻犲鍟弳锝夋煂韫囨挾鎽嶉柟顑跨劍鐏忕喖鐛?
    double alpha_magnitude = cabs(state->alpha);
    double beta_magnitude = cabs(state->beta);
    double alpha_phase = carg(state->alpha);
    double beta_phase = carg(state->beta);
    
    if (match_field_type) {
        // 濠⒀呭仜瀹哥浛lpha闁瑰壊鍨扮粻娆撴晬鐏炶棄娅ょ€殿喚娓秂ta闁瑰壊鍨扮粻?
        alpha_magnitude += field_intensity * 0.1;
        beta_magnitude -= field_intensity * 0.1;
    } else {
        // 闁告垵绻愰幀顧pha闁瑰壊鍨扮粻娆撴晬鐏炵瓔鏉荤€殿喚顕猠ta闁瑰壊鍨扮粻?
        alpha_magnitude -= field_intensity * 0.1;
        beta_magnitude += field_intensity * 0.1;
    }
    
    // 缁绢収鍠曠换姘跺箰椤栨氨鐣介梻鍫㈠仩缁€?
    if (alpha_magnitude < 0.0) alpha_magnitude = 0.0;
    if (beta_magnitude < 0.0) beta_magnitude = 0.0;
    
    // 鐟滅増甯婄粩鎾礌?
    double total = alpha_magnitude * alpha_magnitude + beta_magnitude * beta_magnitude;
    double norm = sqrt(total);
    if (norm > 0.0) {
        alpha_magnitude /= norm;
        beta_magnitude /= norm;
    } else {
        alpha_magnitude = 1.0;
        beta_magnitude = 0.0;
    }
    
    // 闁哄洤鐡ㄩ弻濠囨偐閼哥鍋撴担鐟扮泚妤?
    state->alpha = alpha_magnitude * cos(alpha_phase) + alpha_magnitude * sin(alpha_phase) * I;
    state->beta = beta_magnitude * cos(beta_phase) + beta_magnitude * sin(beta_phase) * I;
    
    return 0; // 闁瑰瓨鍔曟慨?
}

/**
 * 闁告艾鐗嗛懟鐔哥▔閵堝嫰鍤嬮梺鎻掔箰閻℃瑩宕?
 * @param field1 缂佹鍏涚粩瀛樼▔椤忓牆娅ら悗娑欏姇濠р偓
 * @param field2 缂佹鍏涚花鈺傜▔椤忓牆娅ら悗娑欏姇濠р偓
 * @param strategy 闁告艾鐗嗛懟鐔虹驳閺嶎偅娈?
 * @return 闁告艾鐗嗛懟鐔煎触鎼达絾鐣遍柡鍌欏嵆閸ｈ櫣鈧稒鍔曞┃鈧?
 */
QField* quantum_field_merge(QField* field1, QField* field2, MergeStrategy strategy) {
    if (!field1 || !field2) {
        return NULL;
    }

    // 闁告帗绋戠紓鎾诲棘閺夋寧绨?
    QField* merged_field = quantum_field_create(
        strcmp(field1->name, "") != 0 && strcmp(field2->name, "") != 0 ? 
            strcat(strcat(strdup(field1->name), "_"), field2->name) : 
            "merged_field",
        field1->type
    );

    if (!merged_field) {
        return NULL;
    }

    // 閻犱礁澧介悿鍡涘触閸繆瀚欓柛锕佹濞堟垹浠﹂悙绮瑰亾?
    merged_field->type = (field1->intensity > field2->intensity) ? field1->type : field2->type;
    merged_field->dimension = field1->dimension;
    
    // 濠㈣泛绉撮崺妤冪箔椤戣法顏卞☉鎿冧簻濠р偓闁汇劌瀚晶宥夊嫉婢跺骸螡闁绘劗鎳撻崺宀勫触閸繆瀚欓柛?
    for (int i = 0; i < field1->node_count; i++) {
        QFieldNode* node1 = &field1->nodes[i];
        double intensity = node1->intensity;
        
        // 婵☆偀鍋撻柡灞诲劤椤戝洦绂嶇仦濂稿殝闁革箒妗ㄩ懙鎴﹀及椤栨碍鍎婇柡鍫濐槺濞村宕ョ仦鑲╃Т缂傚喚鍠氬▓鎴﹀捶閾忕懓浠?
        for (int j = 0; j < field2->node_count; j++) {
            QFieldNode* node2 = &field2->nodes[j];
            
            // 濠碘€冲€归悘澶愬箥閹冪厒闁烩晝顭堥幃鎾存媴瀹ュ洨鏋傞柣銊ュ濠р偓闁绘劗娅㈢槐婵嬪冀鐟欏嫬绁︾紒娑欑墱閺嗘劙宕ラ崼婵婂珯鐎殿喖鎼€?
            if (node1->x == node2->x && node1->y == node2->y && node1->z == node2->z) {
                switch (strategy) {
                    case MERGE_ADD:
                        intensity = node1->intensity + node2->intensity;
                        break;
                    case MERGE_MULTIPLY:
                        intensity = node1->intensity * node2->intensity;
                        break;
                    case MERGE_MAX:
                        intensity = (node1->intensity > node2->intensity) ? 
                                    node1->intensity : node2->intensity;
                        break;
                    case MERGE_MIN:
                        intensity = (node1->intensity < node2->intensity) ? 
                                    node1->intensity : node2->intensity;
                        break;
                    case MERGE_AVERAGE:
                        intensity = (node1->intensity + node2->intensity) / 2.0;
                        break;
                    default:
                        intensity = node1->intensity;
                        break;
                }
                break;
            }
        }
        
        // 婵烇綀顕ф慨鐐哄礆閺夋寧鍊ゆ鐐舵硾濠р偓
        QFieldNode newNode;
        newNode.x = node1->x;
        newNode.y = node1->y;
        newNode.z = node1->z;
        newNode.intensity = intensity;
        newNode.state = node1->state;
        newNode.position = NULL;  // 濞戞挸鐡ㄥ鍌毭圭€ｎ厾妲搁柨娑樿嫰閻ゅ嫰姊介崨顓犲畨闁圭娲ら幃婊堝嫉婢跺娅忛柛鎰噹閻?
        
        quantum_field_add_node(merged_field, &newNode);
    }
    
    // 婵烇綀顕ф慨鐐电箔椤戣法鐧屽☉鎿冧簻濠р偓濞戞搩鍘惧▓鎴︽偑椤掑倸顥楅柣?
    for (int j = 0; j < field2->node_count; j++) {
        QFieldNode* node2 = &field2->nodes[j];
        
        // 婵☆偀鍋撻柡灞诲劜濡叉悂宕ラ敂鑺バ﹂柣娆樺墰婢规帡鎮欓惂鍝ョ濞戞挸绉村﹢顏嗙箔椤戣法顏卞☉鎿冧簻濠р偓濞戞搩鍙忕槐?
        int unique = 1;
        for (int i = 0; i < field1->node_count; i++) {
            QFieldNode* node1 = &field1->nodes[i];
            if (node1->x == node2->x && node1->y == node2->y && node1->z == node2->z) {
                unique = 0;
                break;
            }
        }
        
        // 濠碘€冲€归悘澶愬及椤栨粌顏柣妤€婀遍崑锝夋晬鐏炴儳娼戦柛鏃傚Т閸╁矂宕ラ崼婵婂珯闁?
        if (unique) {
            QFieldNode newNode;
            newNode.x = node2->x;
            newNode.y = node2->y;
            newNode.z = node2->z;
            newNode.intensity = node2->intensity;
            newNode.state = node2->state;
            newNode.position = NULL;  // 濞戞挸鐡ㄥ鍌毭圭€ｎ厾妲搁柨娑樿嫰閻ゅ嫰姊介崨顓犲畨闁圭娲ら幃婊堝嫉婢跺娅忛柛鎰噹閻?
            
            quantum_field_add_node(merged_field, &newNode);
        }
    }
    
    return merged_field;
}

/**
 * 濞达絽銇樼悮杈ㄧ▔椤忓牆娅ら悗娑欏姇濠р偓闁烩晠鏅茬花鐗堟媴濠婂懏鏆?
 * @param field1 缂佹鍏涚粩瀛樼▔椤忓牆娅ら悗娑欏姇濠р偓
 * @param field2 缂佹鍏涚花鈺傜▔椤忓牆娅ら悗娑欏姇濠р偓
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€0闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛銉у仱閺佸﹦鎷犻婊呭灣
 */
int quantum_field_interact(QField* field1, QField* field2) {
    if (!field1 || !field2) {
        return -1; // 闁告瑥鍊归弳鐔兼煥濞嗘帩鍤?
    }
    
    // 闁糕晞妗ㄧ花顒勫捶閾忕顫﹂柛銊ヮ儓椤撳摜绮诲Δ鍐╃ゲ濞存粍甯婄紞鏃堟偨閵娧囧厙闁?
    double interaction_factor = 0.1; // 濮掓稒顭堥缁樼閵堝嫮闉嶇紒顖滅帛閺?
    
    // 濠碘€冲€归悘澶愬捶閾忕顫﹂柛銊ヮ儑濞村宕ュ畝瀣濠⒀呭仜瀹歌鲸绂嶉妶鍕瀺闁轰礁鐗婇悘?
    if (field1->type == field2->type) {
        interaction_factor = 0.2;
    }
    
    // 閻犱緤绱曢悾濠氬捶閸濆嫮鍘甸梺鎻掔Т瑜版梻绮欑€ｎ亜顔?
    int overlap_count = 0;
    double total_distance = 0.0;
    
    // 闂侇剙绉村缁樼▔閵堝嫰鍤嬮柛锕佹濞堟垿骞嶉埀顒勫嫉婢跺骸螡闁绘劗鎳撻顕€鏁嶇仦缁㈡⒕闁哄被鍎遍悾鐘崇椤掑倹鐣遍柣鈺冾焾椤曨喗鎷呭鍥╂瀭
    for (int i = 0; i < field1->node_count; i++) {
        for (int j = 0; j < field2->node_count; j++) {
            double distance = calculate_distance(
                field1->nodes[i].x, field1->nodes[i].y, field1->nodes[i].z,
                field2->nodes[j].x, field2->nodes[j].y, field2->nodes[j].z
            );
            
            // 閻犵儤绻勯‖鍥╀焊韫囧海鑹鹃梻鍐ㄧ墕閳ь剝澹堥～瀣▔濞差亜娅㈤柛?
            if (distance < 2.0) {
                overlap_count++;
                total_distance += distance;
            }
        }
    }
    
    // 濠碘€冲€归悘澶娾柦閳╁啯绠掗梺鎻掔Т瑜版棃鏁嶅畝鈧ù澶嬬閹哄秶绋婇柣顫姀缁舵繂顕?
    if (overlap_count == 0) {
        interaction_factor *= 0.5;
    } else {
        // 閻犱緤绱曢悾濠氱嵁閸愬弶缍嗛悹鐑樼箘椤洭鏁嶅畝鍐崺缂佸倹妲掔粔铏逛焊韫囥儳绀夐柣鈺呮櫜缁ㄧ増鎷呭鍛殢閻℃帒锕ゅ?
        double avg_distance = total_distance / overlap_count;
        interaction_factor *= (2.0 / (1.0 + avg_distance));
    }
    
    // 闁革箑鎼杈ㄦ償閿旂偓绁插ù婊勫笒婵傛牠宕?
    double field1_new_strength = field1->intensity * (1.0 + interaction_factor * field2->intensity);
    double field2_new_strength = field2->intensity * (1.0 + interaction_factor * field1->intensity);
    
    // 閹煎瓨姊婚弫銈夊棘閺夊灝绻侀幖?
    field1->intensity = field1_new_strength;
    field2->intensity = field2_new_strength;
    
    return 0; // 闁瑰瓨鍔曟慨?
}

/**
 * 闁告瑯鍨甸～瀣礌閺嶎厼娅ら悗娑欏姇濠р偓
 * @param field 闂佹彃绻愰悺娆撳捶?
 * @param filename 閺夊牊鎸搁崵顓㈠棘閸ワ附顐介柛?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€0闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛銉у仱閺佸﹦鎷犻婊呭灣
 */
int quantum_field_visualize(QField* field, const char* filename) {
    if (!field || !filename) {
        return -1; // 闁告瑥鍊归弳鐔兼煥濞嗘帩鍤?
    }
    
    // 闁瑰灚鎸哥槐鎴﹀棘閸ワ附顐?
    FILE* file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "闂佹寧鐟ㄩ銈夋晬濮橆厽锟ユ繛澶嬫礃婢э箑顕ｉ埀顒勫棘閸ワ附顐?%s 閺夆晜绋栭、鎴﹀礃濞嗗繐寮砛n", filename);
        return -2;
    }
    
    // 闁告劖鐟ラ崣鍡涘捶閸濆嫮鍞ㄩ柡鍫厸娣囧﹪骞?
    fprintf(file, "# 闂佹彃绻愰悺娆撳捶閸濆嫬璁查悷娆忔鐎电瀳n");
    fprintf(file, "闁告艾绉惰ⅷ: %s\n", field->name);
    fprintf(file, "缂侇偉顕ч悗? %d\n", field->type);
    fprintf(file, "鐎殿喖鎼€? %.4f\n", field->intensity);
    fprintf(file, "闁煎搫鍊婚崑锝夊极娴兼潙娅? %d\n\n", field->node_count);
    
    // 闁告劖鐟ラ崣鍡椥掕箛搴ㄥ殝闁煎搫鍊婚崑锝夋儍閸曨亙绻嗛柟?
    fprintf(file, "# 闁煎搫鍊婚崑锝夊极閻楀牆绁n");
    fprintf(file, "# 闁哄秶鍘х槐? X Y Z 鐎殿喖鎼€?闁绘鍩栭埀顑挎诞D\n");
    
    for (int i = 0; i < field->node_count; i++) {
        QFieldNode* node = &field->nodes[i];
        fprintf(file, "%.4f %.4f %.4f %.4f", node->x, node->y, node->z, node->intensity);
        
        // 濠碘€冲€归悘澶愭嚍閸屾粌浠柡鍫濐槸閸櫻囨嚂閺冨倸笑闁诡兛绶ょ槐婵囨綇閹惧啿姣夐柣妯垮煐閳ь兛绀侀幃鏇犵矓?
        if (node->state) {
            fprintf(file, " %s", node->state->name);
        } else {
            fprintf(file, " -");
        }
        
        fprintf(file, "\n");
    }
    
    // 闁稿繑濞婂Λ鎾棘閸ワ附顐?
    fclose(file);
    return 0; // 闁瑰瓨鍔曟慨?
} 
