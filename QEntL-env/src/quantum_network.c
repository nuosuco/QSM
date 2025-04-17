/**
 * 闂佹彃绻愰悺娆戠磾閹寸姷鎹曟俊顖椻偓铏仴閻庡湱鍋熼獮? * 
 * 閻庡湱鍋熼獮鍥煂韫囨挾鎽嶇紓鍐╁灩缁爼鎳為崒婊冧化闁告粌鐬煎ù澶愬礂閾忣偅鎯欏ù锝嗗殠閳? * 闁告牕鎳庨幆鍫ユ嚍閸屾粌浠柛鎺撶☉缂傛捇濡存担渚悁闁荤偛妫楅幏鎵磾閹寸姷鎹曢柟鍨С缂嶆棃鎯冮崟顒傚闊洤鍟慨娑㈡嚄婵劏鍋? */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include "quantum_network.h"

/* 闁告劕鎳橀崕瀛樻綇閸涱厼袠闁告垼濮ら弳鐔哥珶閻楀牊顫?*/
static char* generate_readable_id(const uint8_t* id, int length);
static char* generate_network_id();
static void log_network_action(QuantumNetwork* network, const char* action, const char* details);
static char* get_current_timestamp();

/**
 * 闁告帗绋戠紓鎾诲棘閹殿喗鐣遍梺鎻掔箰閻℃瑧绱旈幋鐘垫崟闁煎搫鍊婚崑顤廌
 */
QuantumNetworkNodeID create_network_node_id() {
    QuantumNetworkNodeID node_id;
    
    // 闁汇垻鍠愰崹姘舵⒕韫囨梹绨欼D
    for (int i = 0; i < 32; i++) {
        node_id.id[i] = (uint8_t)(rand() % 256);
    }
    
    // 闁告帗绋戠紓鎾诲矗椤栨繍鍤D闁挎稑鐗嗗畷鍕礂椤擄紕绠婚柛鎺撳劶閵嗗啰绮堥悮瀵哥
    char* readable = generate_readable_id(node_id.id, 32);
    strncpy(node_id.readable_id, readable, 64);
    node_id.readable_id[64] = '\0';  // 缁绢収鍠曠换姘扁偓娑欘殘椤戜焦绋夐懠顒傛尝闁?    free(readable);
    
    return node_id;
}

/**
 * 濞寸姴楠搁悺褏绮敂鑳洬闁告帗绋戠紓鎾绘嚍閸屾粌浠疘D
 */
QuantumNetworkNodeID create_node_id_from_string(const char* id_string) {
    QuantumNetworkNodeID node_id;
    memset(node_id.id, 0, 32);
    
    // 閻忓繐妫楀畷鍕礂椤擄紕绠婚柛鎺曟硾閻⊙呯箔閿旇儻顩弶鐑嗗墯瀹曞弶绋夐崫鍕憻闁煎搫鍊归弳鐔虹磼?    int len = strlen(id_string);
    int bytes = (len + 1) / 2;  // 闁告碍鍨崇粭鍌炲矗閺嶃劍娈?
    
    if (bytes > 32) bytes = 32;  // 闂傚嫭鍔曢崺妤呭嫉閳ь剚寰勮閺嗚鲸鎯?    
    for (int i = 0; i < bytes; i++) {
        int pos = len - i * 2 - 1;
        if (pos >= 0) {
            char hex[3] = {0};
            hex[0] = pos > 0 ? id_string[pos - 1] : '0';
            hex[1] = id_string[pos];
            node_id.id[31 - i] = (uint8_t)strtol(hex, NULL, 16);
        }
    }
    
    // 闁告帗绋戠紓鎾诲矗椤栨繍鍤D
    strncpy(node_id.readable_id, id_string, 64);
    node_id.readable_id[64] = '\0';  // 缁绢収鍠曠换姘扁偓娑欘殘椤戜焦绋夐懠顒傛尝闁?    
    return node_id;
}

/**
 * 婵絾妫佺欢婵囩▔閵堝嫰鍤嬮柤鍝勫€婚崑顤廌
 */
int compare_node_ids(QuantumNetworkNodeID id1, QuantumNetworkNodeID id2) {
    return memcmp(id1.id, id2.id, 32);
}

/**
 * 闁告帗绋戠紓鎾诲棘閹殿喗鐣遍梺鎻掔箰閻℃瑧绱旈幋鐘垫崟闁煎搫鍊婚崑? */
QuantumNetworkNode* create_network_node(QuantumNetworkNodeType type) {
    // 闁告帒妫濋崢銈夊礃閸涱厾鎽?
    QuantumNetworkNode* node = (QuantumNetworkNode*)malloc(sizeof(QuantumNetworkNode));
    if (!node) {
        fprintf(stderr, "闁哄啰濮电涵鍫曞礆閸℃稑甯抽梺鎻掔箰閻℃瑧绱旈幋鐘垫崟闁煎搫鍊婚崑锝夊礃閸涱厾鎽燶n");
        return NULL;
    }
    
    // 闁告帗绻傞～鎰板礌閺嵮呭敤闁哄牜鍓欓惈姗€骞€?    node->id = create_network_node_id();
    node->type = type;
    node->status = NODE_STATUS_INACTIVE;
    
    // 闁告帗绻傞～鎰板礌閺嵮冨笚闁轰胶澧楀畵?    node->metadata.name = strdup("闁哄牜浜滈幊锟犲触瀹ュ牆螡闁?);
    node->metadata.description = strdup("");
    node->metadata.creation_timestamp = get_current_timestamp();
    node->metadata.last_update_timestamp = strdup(node->metadata.creation_timestamp);
    node->metadata.creator_id = strdup("system");
    node->metadata.version = 1;
    node->metadata.tags = strdup("");
    node->metadata.location = strdup("闁哄牜浜為悡鈩冩媴瀹ュ洨鏋?);
    
    // 闁告帗绻傞～鎰板礌閺嶎剛绠鹃柟?    node->connections = NULL;
    node->connection_count = 0;
    node->connection_capacity = 0;
    
    // 闁告帗绻傞～鎰板礌閺嶎剙螡闁绘劗鎳撻惈姗€骞€?    node->processing_capacity = 1.0;
    node->storage_capacity = 1.0;
    node->coherence_time = 1000.0;  // 濮掓稒顭堥?000ms
    node->error_rate = 0.01;  // 濮掓稒顭堥?%闁汇劌瀚伴弫濠勬嫚椤栨粌鑺?
    
    // 闁告帗绻傞～鎰板礌閺嶎収鏉哄鑸电墧娣囧﹪骞?    node->node_context = NULL;
    node->node_process = NULL;
    
    // 闁哄秷顫夊畵浣虹尵鐠囪尙鈧兘宕氬┑鍡╂綏闁告牗鐗曢崬瀵糕偓?    switch (type) {
        case NETWORK_NODE_TYPE_STATE:
            node->content.state = NULL;
            break;
        case NETWORK_NODE_TYPE_ENTANGLEMENT:
            node->content.channel = NULL;
            break;
        case NETWORK_NODE_TYPE_FIELD:
            node->content.field = NULL;
            break;
        default:
            node->content.custom_data = NULL;
            break;
    }
    
    printf("鐎瑰憡褰冮崹鍗烆嚈濞差亜娅ら悗娑欏姉缂嶅绱掑鍡椢濋柣?(ID: %s, 缂侇偉顕ч悗? %d)\n", node->id.readable_id, type);
    return node;
}

/**
 * 闁告帗绋戠紓鎾绘煂韫囨挾鎽嶉柟顑挎祰婵☆參鎮? */
QuantumNetworkNode* create_quantum_state_node(QuantumState* state) {
    if (!state) return NULL;
    
    QuantumNetworkNode* node = create_network_node(NETWORK_NODE_TYPE_STATE);
    if (!node) return NULL;
    
    // 閻犱礁澧介悿鍡涙煂韫囨挾鎽嶉柟?    node->content.state = state;
    
    // 閻犱礁澧介悿鍡涙嚍閸屾粌浠柛姘Ф琚ㄩ柛婊冩湰瀵寧娼?    free(node->metadata.name);
    free(node->metadata.description);
    
    node->metadata.name = strdup("闂佹彃绻愰悺娆撳箑娴ｈ棄螡闁?);
    char desc[256];
    snprintf(desc, sizeof(desc), "闁告牕鎳庨幆?d闂佹彃绻愰悺娆徯掗弮鍌氼棗闁汇劌瀚伴崳铏光偓娑欏姈閳ь兛娴囨俊顓㈡倷?, state->qubit_count);
    node->metadata.description = strdup(desc);
    
    return node;
}

/**
 * 闁告帗绋戠紓鎾剁棯閻樼數鐐婇柤鍝勫€婚崑? */
QuantumNetworkNode* create_entanglement_node(EntanglementChannel* channel) {
    if (!channel) return NULL;
    
    QuantumNetworkNode* node = create_network_node(NETWORK_NODE_TYPE_ENTANGLEMENT);
    if (!node) return NULL;
    
    // 閻犱礁澧介悿鍡欑棯閻樼數鐐婇梺顐ｅ哺娴?    node->content.channel = channel;
    
    // 閻犱礁澧介悿鍡涙嚍閸屾粌浠柛姘Ф琚ㄩ柛婊冩湰瀵寧娼?    free(node->metadata.name);
    free(node->metadata.description);
    
    node->metadata.name = strdup("缂佸墽濮风槐鍫曟嚍閸屾粌浠?);
    char desc[256];
    snprintf(desc, sizeof(desc), "闁告牕鎳庨幆鍫㈢尵鐠囪尙鈧攱绋?d闁汇劌瀚猾鍌滅磽閻樼儵鍋撳鏈靛闁煎搫鍊婚崑?, channel->type);
    node->metadata.description = strdup(desc);
    
    // 閻犱礁澧介悿鍡涙儎缁嬪灝鍙￠柡鍐ㄧ埣濡寧绋夋惔銊㈠亾濮樻湹澹曞☉鎾亾闁?    node->coherence_time = channel->coherence_time;
    
    return node;
}

/**
 * 闁告帗绋戠紓鎾绘煂韫囨挾鎽嶉柛锕傜細婵☆參鎮? */
QuantumNetworkNode* create_quantum_field_node(QField* field) {
    if (!field) {
        fprintf(stderr, "闂佹寧鐟ㄩ銈夋晬濮橆厽锟ユ繛澶嬫礀閸ㄥ崬顕欏ú顏勬閻庢稒鍔曞┃鈧柤鍝勫€婚崑锝夋晬鐏炶姤绨氬☉鎾剁樁ULL\n");
        return NULL;
    }
    
    QuantumNetworkNode* node = create_network_node(NETWORK_NODE_TYPE_FIELD);
    if (!node) return NULL;
    
    node->content.field = field;
    
    // 閻犱礁澧介悿鍡涙嚍閸屾粌浠柛姘Ф琚ㄩ柛婊冩湰瀵寧娼?    QFieldMetadata field_metadata = get_field_metadata(field);
    if (field_metadata.name) {
        set_node_name(node, field_metadata.name);
    } else {
        set_node_name(node, "闁告牕鐏濋幃鏇㈡煂韫囨挾鎽嶉柛?);
    }
    
    if (field_metadata.description) {
        set_node_description(node, field_metadata.description);
    } else {
        set_node_description(node, "闂佹彃绻愰悺娆撳捶妤﹀灝螡闁?);
    }
    
    return node;
}

/**
 * 闂佹彃锕ラ弬渚€鏌岃箛鎾舵憤缂傚啯鍨圭划鍫曟嚍閸屾粌浠悹褍瀚花? */
void free_network_node(QuantumNetworkNode* node) {
    if (!node) return;
    
    // 闂佹彃锕ラ弬渚€宕楅崘鈺傛闁?    free(node->metadata.name);
    free(node->metadata.description);
    free(node->metadata.creation_timestamp);
    free(node->metadata.last_update_timestamp);
    free(node->metadata.creator_id);
    free(node->metadata.tags);
    free(node->metadata.location);
    
    // 闂佹彃锕ラ弬浣规交閻愭潙澶?
    for (int i = 0; i < node->connection_count; i++) {
        free(node->connections[i]);
    }
    free(node->connections);
    
    // 闂佹彃锕ラ弬渚€鎳為崒婊冧化闁哄牜鍓濋棅?    free(node);
    
    printf("鐎瑰憡鐓￠崳鎾绩妤ｅ啫娅ら悗娑欏姉缂嶅绱掑鍡椢濋柣鎰攰缁侇偄鈹冮幀绲?);
}

/**
 * 闁告帗绋戠紓鎾绘煂韫囨挾鎽嶇紓鍐╁灩缁? */
QuantumNetwork* create_quantum_network(const char* name, int initial_capacity) {
    // 闁告帒妫濋崢銈夊礃閸涱厾鎽?
    QuantumNetwork* network = (QuantumNetwork*)malloc(sizeof(QuantumNetwork));
    if (!network) {
        fprintf(stderr, "闁哄啰濮电涵鍫曞礆閸℃稑甯抽梺鎻掔箰閻℃瑧绱旈幋鐘垫崟闁告劕鎳庨悺鈺榥");
        return NULL;
    }
    
    // 闁告帗绻傞～鎰板礌閺嵮呭敤闁哄牜鍓欓惈姗€骞€?    network->network_id = generate_network_id();
    network->network_name = strdup(name ? name : "闁哄牜浜滈幊锟犲触瀹ュ娅ら悗娑欏姉缂嶅绱?);
    network->creation_time = time(NULL);
    network->node_count = 0;
    network->capacity = initial_capacity > 0 ? initial_capacity : 10;
    
    // 闁告帒妫濋崢銈夋嚍閸屾粌浠柡浣瑰缁?    network->nodes = (QuantumNetworkNode**)malloc(sizeof(QuantumNetworkNode*) * network->capacity);
    if (!network->nodes) {
        fprintf(stderr, "闁哄啰濮电涵鍫曞礆閸℃稑甯抽柤鍝勫€婚崑锝夊极閹殿喚鐭嬮柛鎰噹閻♀晿n");
        free(network->network_name);
        free(network->network_id);
        free(network);
        return NULL;
    }
    
    // 闁告帗绻傞～鎰板礌閺嶎剙螡闁绘劘顫夐弳鐔虹磼?    for (int i = 0; i < network->capacity; i++) {
        network->nodes[i] = NULL;
    }
    
    // 闁告帗绋戠紓鎾剁棯閻樼數鐐婂Δ鐘妼閸忚京绱旈幋鐘垫崟
    network->entanglement_backbone = create_entanglement_network(initial_capacity);
    if (!network->entanglement_backbone) {
        fprintf(stderr, "闁哄啰濮电涵鍫曞礆濞戞绱︾紒鍓уХ缁辫埖顨ラ妸銉ュ彙缂傚啯鍨圭划绂眓");
        free(network->nodes);
        free(network->network_name);
        free(network->network_id);
        free(network);
        return NULL;
    }
    
    printf("鐎瑰憡褰冮崹鍗烆嚈濞差亜娅ら悗娑欏姉缂嶅绱? %s (ID: %s)\n", network->network_name, network->network_id);
    return network;
}

/**
 * 闂佹彃锕ラ弬渚€鏌岃箛鎾舵憤缂傚啯鍨圭划鍓佹導閸曨剛鐖?
 */
void free_quantum_network(QuantumNetwork* network) {
    if (!network) return;
    
    // 閻犱焦婢樼紞宥夊箼瀹ュ嫮绋?
    log_network_action(network, "闁稿繑濞婂Λ?, "闂佹彃锕ラ弬渚€鏌岃箛鎾舵憤缂傚啯鍨圭划鍓佹導閸曨剛鐖?);
    
    // 闂佹彃锕ラ弬渚€骞嶉埀顒勫嫉婢跺骸螡闁?    for (int i = 0; i < network->node_count; i++) {
        if (network->nodes[i]) {
            free_network_node(network->nodes[i]);
        }
    }
    
    // 闂佹彃锕ラ弬浣虹棯閻樼數鐐婂Δ鐘妼閸忚京绱旈幋鐘垫崟
    if (network->entanglement_backbone) {
        free_entanglement_network(network->entanglement_backbone);
    }
    
    // 闂佹彃锕ラ弬渚€鎳為崒婊冧化闁轰焦澹嗙划?    free(network->nodes);
    
    // 闂佹彃锕ラ弬浣虹磾閹寸姷鎹旾D闁告粌鑻幃鏇犵矓?    free(network->network_id);
    free(network->network_name);
    
    // 闂佹彃锕ラ弬浣虹磾閹寸姷鎹曢柡鍫墲闂?    free(network);
    
    printf("鐎瑰憡鐓￠崳鎾绩妤ｅ啫娅ら悗娑欏姉缂嶅绱掑鍡欍偒婵犙勨偓绲?);
}

/**
 * 閻犱礁澧介悿鍡涙嚍閸屾粌浠柛蹇撳暞閺嗙喖骞? */
void set_node_metadata(QuantumNetworkNode* node, QuantumNetworkNodeMetadata metadata) {
    if (!node) return;
    
    // 闂佹彃锕ラ弬渚€寮閸樻捇寮悧鍫濈ウ
    free(node->metadata.name);
    free(node->metadata.description);
    free(node->metadata.tags);
    free(node->metadata.location);
    
    // 閻犱礁澧介悿鍡涘棘閺夊灝甯楅柡浣哄瀹?    node->metadata.name = strdup(metadata.name ? metadata.name : "闁哄牜浜滈幊锟犲触瀹ュ牆螡闁?);
    node->metadata.description = strdup(metadata.description ? metadata.description : "");
    node->metadata.tags = strdup(metadata.tags ? metadata.tags : "");
    node->metadata.location = strdup(metadata.location ? metadata.location : "闁哄牜浜為悡鈩冩媴瀹ュ洨鏋?);
    
    // 闁哄洤鐡ㄩ弻濠囨偋閸喐鎷遍柛婊冩湰濡炲倿姊荤€涙ê鐓?
    node->metadata.version++;
    free(node->metadata.last_update_timestamp);
    node->metadata.last_update_timestamp = get_current_timestamp();
    
    printf("鐎圭寮跺ú鍧楀棘閹峰苯螡闁绘劗鎳撻崢鎾诲极閻楀牆绁? %s (ID: %s)\n", node->metadata.name, node->id.readable_id);
}

/**
 * 闁兼儳鍢茶ぐ鍥嚍閸屾粌浠柛蹇撳暞閺嗙喖骞? */
QuantumNetworkNodeMetadata get_node_metadata(QuantumNetworkNode* node) {
    QuantumNetworkNodeMetadata empty_metadata = {0};
    
    if (!node) return empty_metadata;
    
    return node->metadata;
}

/**
 * 闁哄洤鐡ㄩ弻濠囨嚍閸屾粌浠柣妯垮煐閳? */
QuantumNetworkError update_node_status(QuantumNetworkNode* node, NodeStatus new_status) {
    if (!node) return NETWORK_ERROR_INVALID_ARGUMENT;
    
    // 閻犱焦婢樼紞宥夊籍瑜忔慨鎼佸箑?    NodeStatus old_status = node->status;
    
    // 闁哄洤鐡ㄩ弻濠囨偐閼哥鍋?    node->status = new_status;
    
    // 闁哄洤鐡ㄩ弻濠囧籍閸洘锛熼柟?    free(node->metadata.last_update_timestamp);
    node->metadata.last_update_timestamp = get_current_timestamp();
    
    printf("闁煎搫鍊婚崑锝夋偐閼哥鍋撴担绋垮殥濞?%d 闁哄洤鐡ㄩ弻濠冪▔?%d (ID: %s)\n", 
           old_status, new_status, node->id.readable_id);
    
    return NETWORK_ERROR_NONE;
}

/**
 * 闁告碍鍨圭紞澶岀磼濠婂嫬娼戦柛鏃傚Ь婵☆參鎮? */
QuantumNetworkError add_node_to_network(QuantumNetwork* network, QuantumNetworkNode* node) {
    if (!network || !node) return NETWORK_ERROR_INVALID_ARGUMENT;
    
    // 婵☆偀鍋撻柡灞诲劥婵☆參鎮欑憴鍕﹂柛姘剧畱閸戯紕鈧稒锚濠€?    for (int i = 0; i < network->node_count; i++) {
        if (compare_node_ids(network->nodes[i]->id, node->id) == 0) {
            return NETWORK_ERROR_NODE_ALREADY_EXISTS;
        }
    }
    
    // 婵☆偀鍋撻柡灞诲劚椤旀劙鏌?    if (network->node_count >= network->capacity) {
        // 闁圭鏅涢惈宥団偓鐟扮秺閸?        int new_capacity = network->capacity * 2;
        QuantumNetworkNode** new_nodes = (QuantumNetworkNode**)realloc(
                                        network->nodes, 
                                        sizeof(QuantumNetworkNode*) * new_capacity);
        
        if (!new_nodes) {
            return NETWORK_ERROR_MEMORY_ALLOCATION;
        }
        
        network->nodes = new_nodes;
        
        // 闁告帗绻傞～鎰板礌閺嶃劍鐓€缂佸本妞藉Λ?        for (int i = network->capacity; i < new_capacity; i++) {
            network->nodes[i] = NULL;
        }
        
        network->capacity = new_capacity;
    }
    
    // 婵烇綀顕ф慨鐐烘嚍閸屾粌浠?
    network->nodes[network->node_count] = node;
    network->node_count++;
    
    // 闁哄洤鐡ㄩ弻濠囨嚍閸屾粌浠柣妯垮煐閳?    update_node_status(node, NODE_STATUS_ACTIVE);
    
    // 閻犱焦婢樼紞宥夊箼瀹ュ嫮绋?
    char details[256];
    snprintf(details, sizeof(details), "婵烇綀顕ф慨鐐烘嚍閸屾粌浠?(ID: %s, 缂侇偉顕ч悗? %d)", 
             node->id.readable_id, node->type);
    log_network_action(network, "婵烇綀顕ф慨鐐烘嚍閸屾粌浠?, details);
    
    printf("鐎瑰憡褰冮幃婊呯磾閹寸姷鎹?%s 婵烇綀顕ф慨鐐烘嚍閸屾粌浠?(ID: %s)\n", 
           network->network_name, node->id.readable_id);
    
    return NETWORK_ERROR_NONE;
}

/* 闁告劕鎳橀崕瀛樻綇閸涱厼袠闁告垼濮ら弳鐔衡偓鍦仧楠?*/

/**
 * 闁汇垻鍠愰崹姘跺矗椤栨繍鍤D
 */
static char* generate_readable_id(const uint8_t* id, int length) {
    char* readable = (char*)malloc(length * 2 + 1);
    if (!readable) return NULL;
    
    for (int i = 0; i < length; i++) {
        sprintf(readable + i * 2, "%02x", id[i]);
    }
    readable[length * 2] = '\0';
    
    return readable;
}

/**
 * 闁汇垻鍠愰崹姘辩磾閹寸姷鎹旾D
 */
static char* generate_network_id() {
    uint8_t id[16];
    
    // 闁汇垻鍠愰崹姘舵⒕韫囨梹绨欼D
    for (int i = 0; i < 16; i++) {
        id[i] = (uint8_t)(rand() % 256);
    }
    
    return generate_readable_id(id, 16);
}

/**
 * 閻犱焦婢樼紞宥囩磾閹寸姷鎹曢柟鍨С缂? */
static void log_network_action(QuantumNetwork* network, const char* action, const char* details) {
    if (!network || !action || !details) return;
    
    // 閻庡湱鍋ゅ顖涖亜閸︻厽绐楀☉鎿冨弨缁绘牠鏌岀仦鐣屽畨閻犲洢鍎遍悿鍕偝閻楀牊锛夐煫鍥殙椤斿洩銇?    // 濞戞捁妗ㄧ花锛勭不閳ь剟宕￠弴鈩冨闯閻熸瑤绶ょ槐婵囨交濞嗘挸娅￠柛娆樹簼婢э箓宕￠弶鍨厒闁硅矇鍐ㄧ厬闁?    char timestamp[64];
    time_t now = time(NULL);
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", localtime(&now));
    
    printf("[%s] 缂傚啯鍨圭划? %s (ID: %s) - 闁瑰灝绉崇紞? %s - %s\n",
           timestamp, network->network_name, network->network_id, action, details);
}

/**
 * 闁兼儳鍢茶ぐ鍥亹閹惧啿顤呴柡鍐ㄧ埣濡潡骞? */
static char* get_current_timestamp() {
    char* timestamp = (char*)malloc(64);
    if (!timestamp) return NULL;
    
    time_t now = time(NULL);
    strftime(timestamp, 64, "%Y-%m-%d %H:%M:%S", localtime(&now));
    
    return timestamp;
} 
