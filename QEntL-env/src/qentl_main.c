/*
 * QEntl闂佹彃绻愰悺娆戠磽閺嶎偀鏌ら柣婊庡灠椤ｃ劎鎲撮敐澶婃珵闁革絻鍔岄崣鍡涘矗閿濆洠鏌ら幖?
 * 闁绘鐗婂﹢浼存晬?.0
 * 闁哄啨鍎插﹢锟犳晬?024-05-20
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "quantum_state.h"
#include "quantum_entanglement.h"
#include "quantum_gene.h"
#include "quantum_field.h"
#include "quantum_field_generator.h"

// 闁绘鐗婂﹢鐗堢┍閳╁啩绱?
#define QENTL_VERSION "1.0.0"
#define QENTL_BUILD_DATE "2024-05-20"

// 闁告稒鍨濋幎銈囨偘瀹€鍕ㄥ亾婢舵劑鈧?
typedef struct {
    int verbose;            // 闁哄嫷鍨伴幆浣规綇閹惧啿姣夐悹鍥峰缁繑绌遍埄鍐х礀
    int interactive;        // 闁哄嫷鍨伴幆浣规交濞戞ê寮冲ù婧垮€撶花鏉课熼垾宕囩
    char input_file[256];   // 閺夊牊鎸搁崣鍡涘棘閸ワ附顐介柛?
    char output_file[256];  // 閺夊牊鎸搁崵顓㈠棘閸ワ附顐介柛?
    int generate_field;     // 闁哄嫷鍨伴幆渚€鎮介悢绋跨亣闂佹彃绻愰悺娆撳捶?
    int test_mode;          // 闁哄嫷鍨伴幆浣瑰緞閸曨亞鑹炬繛鏉戭儓閻︻垰螣閳ュ磭纭€
} CommandOptions;

// 闁告垼濮ら弳鐔煎礈瀹ュ懏鍊诲鍦濡?
void print_version();
void print_help();
void print_banner();
int parse_arguments(int argc, char* argv[], CommandOptions* options);
int run_interactive_mode();
int run_file_mode(const char* filename, const CommandOptions* options);
int generate_quantum_field(const char* output_file, const CommandOptions* options);
int run_test(const char* test_file);

/**
 * 缂佸顑呯花顓㈠礂閵夈儱缍撻柣?
 */
int main(int argc, char* argv[]) {
    // 閻犱礁澧介悿鍡涘箳瑜嶉崺妤呭矗閹殿喚妞介柣顔绘鐠愮兙TF-8
    #ifdef _WIN32
    system("chcp 65001 > nul");
    #endif
    
    // 閻熸瑱绲鹃悗浠嬪川閹存帗濮㈤悶娑樿嫰瀵剟寮?
    CommandOptions options = {0};
    int result = parse_arguments(argc, argv, &options);
    
    if (result != 0) {
        return result;
    }
    
    // 闁哄秷顫夊畵渚€宕ㄩ幋鎺撳Б閻炴稑鐭傞埀顒€顦甸妴宥夊箥瑜戦、鎴︽儎缁嬭法瀹夐柟鍨С缂?
    if (options.test_mode) {
        // 婵炴潙顑堥惁顖毼熼垾宕囩
        return run_test(options.input_file);
    } else if (options.generate_field) {
        // 闁汇垻鍠愰崹姘舵煂韫囨挾鎽嶉柛锔惧劋鑶╃€?
        return generate_quantum_field(options.output_file, &options);
    } else if (options.interactive) {
        // 濞存嚎鍊撶花鏉课熼垾宕囩
        return run_interactive_mode();
    } else if (options.input_file[0] != '\0') {
        // 闁哄倸娲ｅ▎銏㈡喆閿濆娅炴俊顖椻偓宕囩
        return run_file_mode(options.input_file, &options);
    } else {
        // 婵炲备鍓濆﹢渚€骞愰崶褏鏆板ù鐘侯唺缂嶅秹骞欏鍕▕闁挎稑鏈Ο澶岀矆閸濆嫬绨婚柛鏂烘櫃娣囧﹪骞?
        print_help();
        return 0;
    }
}

/**
 * 閻熸瑱绲鹃悗浠嬪川閹存帗濮㈤悶娑樿嫰瀵剟寮?
 */
int parse_arguments(int argc, char* argv[], CommandOptions* options) {
    if (argc < 2) {
        print_help();
        return 1;
    }
    
    // 濮掓稒顭堥濠氬磹?
    options->verbose = 0;
    options->interactive = 0;
    options->generate_field = 0;
    options->test_mode = 0;
    options->input_file[0] = '\0';
    options->output_file[0] = '\0';
    
    // 閻熸瑱绲鹃悗浠嬪矗閸屾稒娈?
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--version") == 0 || strcmp(argv[i], "-v") == 0) {
            print_version();
            return 1;
        } else if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            print_help();
            return 1;
        } else if (strcmp(argv[i], "--interactive") == 0 || strcmp(argv[i], "-i") == 0) {
            options->interactive = 1;
        } else if (strcmp(argv[i], "--verbose") == 0) {
            options->verbose = 1;
        } else if (strcmp(argv[i], "--generate-field") == 0 || strcmp(argv[i], "-g") == 0) {
            options->generate_field = 1;
            
            // 婵☆偀鍋撻柡灞诲劜濡叉悂宕ラ敂鑺ョ畳濞戞挸顑勭粩瀛樼▔椤忓嫬妫橀柡渚€顣︾紞鏃€绋夋ウ璺ㄧ炕闁告垹鍎ら弸鍐╃?
            if (i + 1 < argc && argv[i+1][0] != '-') {
                strcpy(options->output_file, argv[i+1]);
                i++; // 閻犲搫鐤囩换鍐╃▔鐎ｂ晝顏卞☉鎿冧簻瀵剟寮?
            } else {
                fprintf(stderr, "闂佹寧鐟ㄩ銈夋晬?-generate-field 闂侇偄顦甸妴宥夋閳ь剛鎲版担鐟扮樄閻庤淇虹欢顓㈠礄閻戞ɑ鐎ù鐘烘硾閹槥n");
                return 1;
            }
        } else if (strcmp(argv[i], "--output") == 0 || strcmp(argv[i], "-o") == 0) {
            // 婵☆偀鍋撻柡灞诲劜濡叉悂宕ラ敂鑺ョ畳濞戞挸顑勭粩瀛樼▔椤忓嫬妫橀柡渚€顣︾紞鏃€绋夋ウ璺ㄧ炕闁告垹鍎ら弸鍐╃?
            if (i + 1 < argc && argv[i+1][0] != '-') {
                strcpy(options->output_file, argv[i+1]);
                i++; // 閻犲搫鐤囩换鍐╃▔鐎ｂ晝顏卞☉鎿冧簻瀵剟寮?
            } else {
                fprintf(stderr, "闂佹寧鐟ㄩ銈夋晬?-output 闂侇偄顦甸妴宥夋閳ь剛鎲版担鐟扮樄閻庤淇虹欢顓㈠礄閻戞ɑ鐎ù鐘烘硾閹槥n");
                return 1;
            }
        } else if (strcmp(argv[i], "--test") == 0 || strcmp(argv[i], "-t") == 0) {
            options->test_mode = 1;
            
            // 婵☆偀鍋撻柡灞诲劜濡叉悂宕ラ敂鑺ョ畳濞戞挸顑勭粩瀛樼▔椤忓嫬妫橀柡渚€顣︾紞鏃€绋夐悜妯笺偞閻犲洦娲橀弸鍐╃?
            if (i + 1 < argc && argv[i+1][0] != '-') {
                strcpy(options->input_file, argv[i+1]);
                i++; // 閻犲搫鐤囩换鍐╃▔鐎ｂ晝顏卞☉鎿冧簻瀵剟寮?
            }
        } else if (argv[i][0] == '-') {
            fprintf(stderr, "闂佹寧鐟ㄩ銈夋晬濮橆厽寮撻柣顓滃劦閳ь剙顦甸妴?%s\n", argv[i]);
            return 1;
        } else {
            // 闁稿娲╅鏇㈠及椤栨繄缈婚柛蹇嬪劜閺嬪啯绂?
            strcpy(options->input_file, argv[i]);
        }
    }
    
    return 0;
}

/**
 * 閺夊牊鎸搁崵顓㈡偋閸喐鎷卞ǎ鍥ｅ墲娴?
 */
void print_version() {
    printf("QEntl 闂佹彃绻愰悺娆戠磽閺嶎偀鏌ら柣婊庡灠椤ｃ劎鎲撮敐澶婃珵闁?闁绘鐗婂﹢?%s (闁哄瀚紓鎾诲籍閵夛附鍩? %s)\n", 
           QENTL_VERSION, QENTL_BUILD_DATE);
    printf("闁绘鐗婂鍫ュ箥閳ь剟寮?濠?2024 闂佹彃绻愰悺娆徫熼垾宕団偓鐑芥儘閺冨倵鏁€缂備礁鍨瀗");
}

/**
 * 閺夊牊鎸搁崵顓犳暜椤旂厧袠濞ｅ洠鍓濇导?
 */
void print_help() {
    printf("QEntl 闂佹彃绻愰悺娆戠磽閺嶎偀鏌ら柣婊庡灠椤ｃ劎鎲撮敐澶婃珵闁革絺鏅縩");
    printf("闁活潿鍔嶇涵? qentl [闂侇偄顦甸妴宄?[闁哄倸娲ｅ▎顣僜n\n");
    printf("闂侇偄顦甸妴?\n");
    printf("  -h, --help           闁哄嫬澧介妵姘潰閵堝懎绨婚柛鏂烘櫃娣囧﹪骞侀惀濯?);
    printf("  -v, --version        闁哄嫬澧介妵姘舵偋閸喐鎷卞ǎ鍥ｅ墲娴煎尲n");
    printf("  -i, --interactive    闁告凹鍨版慨鈺傜閵堝嫮闉嶆俊顖椻偓宕囩\n");
    printf("  -o, --output FILE    闁圭娲ら悾鐐綇閹惧啿姣夐柡鍌氭矗濞嗩晜n");
    printf("  -g, --generate-field FILE  闁汇垻鍠愰崹姘舵煂韫囨挾鎽嶉柛锕€鎼懟鐔哥┍濠靛棛鎽犻柛鎺斿鐎垫氨鈧纰嶉弸鍐╃缁傜湏");
    printf("  -t, --test [FILE]    閺夆晜鍔橀、鎴澝圭€ｎ厾妲搁柨娑樼墕瑜版煡鏌呮径瀣樄閻庤纰嶇粊瀵告嫚閺囩喐鐎ù鐘侯啇缁辨瓡n");
    printf("  --verbose            閺夊牊鎸搁崵顓犳嫚閿斿墽鐭庡ǎ鍥ｅ墲娴煎尲n\n");
    printf("缂佲偓鏉炴壆浼?\n");
    printf("  qentl program.qentl       閻熸瑱缍侀崳鎾箥瑜戦、鎴犵矙鐎ｎ亞纰嶉柡鍌氭矗濞嗩晜n");
    printf("  qentl -i                  闁告凹鍨版慨鈺傜閵堝嫮闉嶆俊顖椻偓宕囩\n");
    printf("  qentl -g field.qf         闁汇垻鍠愰崹姘舵煂韫囨挾鎽嶉柛锔绢嚔n");
    printf("  qentl -t test_state       闁圭瑳鍡╂斀闁圭娲ら悾鎯圭€ｎ厾妲竆n");
}

/**
 * 閺夊牊鎸搁崵顓炩枎閵忥絿绠ｆ俊顖ｄ簻缁?
 */
void print_banner() {
    printf("  ___  _____      _   _     \n");
    printf(" / _ \\| ____|_ __| |_| |    \n");
    printf("| | | |  _| | '_ \\ __| |    \n");
    printf("| |_| | |___| | | | |_| |   \n");
    printf(" \\__\\_\\_____|_| |_|\\__|_|   \n");
    printf("                            \n");
    printf("闂佹彃绻愰悺娆戠磽閺嶎偀鏌ら柣婊庡灠椤ｃ劎鎲撮敐澶婃珵闁?v%s\n", QENTL_VERSION);
    printf("閺夊牊鎸搁崣?'help' 闁兼儳鍢茶ぐ鍥川閹存帗濮㈤柛鎺擃殙閵嗗啴鏁嶅畝鍐炕闁?'exit' 闂侇偀鍋撻柛鎴炰航閳ь兛绻恘");
    printf("------------------------------------\n");
}

/**
 * 閺夆晜鍔橀、鎴炵閵堝嫮闉嶆俊顖椻偓宕囩
 */
int run_interactive_mode() {
    print_banner();
    
    char input[1024];
    while (1) {
        printf("qentl> ");
        if (fgets(input, sizeof(input), stdin) == NULL) {
            break;
        }
        
        // 闁告ê顭峰▍搴ㄥ箲閵忥綆鏀界紒?
        input[strcspn(input, "\n")] = '\0';
        
        // 濠㈣泛瀚幃濠囨焻閳ь剟宕欓崫鍕殥濞?
        if (strcmp(input, "exit") == 0 || strcmp(input, "quit") == 0) {
            break;
        }
        
        // 濠㈣泛瀚幃濠勬暜椤旂厧袠闁告稒鍨濋幎?
        if (strcmp(input, "help") == 0) {
            printf("闁告瑯鍨抽弫銈夊川閹存帗濮?\n");
            printf("  help                  闁哄嫬澧介妵姘潰閵堝懎绨婚柛鏂烘櫃娣囧﹪骞侀惀濯?);
            printf("  exit, quit            闂侇偀鍋撻柛鎴︾細琚欓梺鎻掞工濞呮妰n");
            printf("  version               闁哄嫬澧介妵姘舵偋閸喐鎷卞ǎ鍥ｅ墲娴煎尲n");
            printf("  load <闁哄倸娲ｅ▎?           闁告梻濮惧ù鍥嵁閼搁潧鈷旈悶娑樼焸閸ｈ櫣鈧稒鍔楅埢鍏兼償韫囨梹鐎ù鐘滴");
            printf("  generate <闁哄倸娲ｅ▎?       闁汇垻鍠愰崹姘舵煂韫囨挾鎽嶉柛锕€鎼懟鐔哥┍濠靛棛鎽犻柛鎺斿閺嬪啯绂掔粋鐪?);
            printf("  clear                 婵炴挸鎳庨惈鍝眓");
            continue;
        }
        
        // 濠㈣泛瀚幃濠囨偋閸喐鎷遍柛娑欏灊閹?
        if (strcmp(input, "version") == 0) {
            print_version();
            continue;
        }
        
        // 濠㈣泛瀚幃濠傘€掗崨顓犳綄闁告稒鍨濋幎?
        if (strcmp(input, "clear") == 0) {
            #ifdef _WIN32
            system("cls");
            #else
            system("clear");
            #endif
            print_banner();
            continue;
        }
        
        // 濠㈣泛瀚幃濠囧礉閻樼儤绁伴柡鍌氭矗濞嗐垽宕ㄩ幋鎺撳Б
        if (strncmp(input, "load ", 5) == 0) {
            char* filename = input + 5;
            CommandOptions options = {0};
            options.verbose = 1;
            printf("闁告梻濮惧ù鍥棘閸ワ附顐介柨?s\n", filename);
            run_file_mode(filename, &options);
            continue;
        }
        
        // 濠㈣泛瀚幃濠囨偨閻旂鐏囬梺鎻掔箰閻℃瑩宕烽崫鍕殥濞?
        if (strncmp(input, "generate ", 9) == 0) {
            char* filename = input + 9;
            CommandOptions options = {0};
            options.verbose = 1;
            printf("闁汇垻鍠愰崹姘舵煂韫囨挾鎽嶉柛锕€鎼懟鐔哥┍濠靛棛鎽犻柛鎺戝簻缁?s\n", filename);
            generate_quantum_field(filename, &options);
            continue;
        }
        
        // 闁圭瑳鍡╂斀闂佹彃绻愰悺娆戞嫚椤撯檧鏋呴柛娑欏灊閹?
        printf("闁圭瑳鍡╂斀: %s\n", input);
        // 闁革负鍔忕换鏍煂鐏炵晫鏉介柣婊€鍗抽崳铏光偓娑欏姌椤曘垻鎳涢埀顒傛喆閿濆娅為梺顐ｆ缁?
        printf("闁哄棗鍊风粭澶愬绩椤栨稑鐦柣鈺佺摠鐢挳骞嶈椤㈡垿鏌岃箛鎾舵憤閻犲浂鍙€閳诲牓宕ㄩ幋鎺撳Б闁靛棗鍊介顒佹媴鐠恒劍鏆弆oad闁告稒鍨濋幎銈夊礉閻樼儤绁伴柡鍌氭矗濞嗐垽濡存穱鎼?);
    }
    
    return 0;
}

/**
 * 閺夆晜鍔橀、鎴﹀棘閸ワ附顐芥俊顖椻偓宕囩
 */
int run_file_mode(const char* filename, const CommandOptions* options) {
    if (options->verbose) {
        printf("閻熸瑱缍侀崳鎾箥瑜戦、鎴﹀棘閸ワ附顐? %s\n", filename);
    }
    
    // 闁瑰灚鎸哥槐鎴﹀棘閸ワ附顐?
    FILE* file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "闂佹寧鐟ㄩ銈夋晬濮橆厽锟ユ繛澶嬫礃婢э箑顕ｉ埀顒勫棘閸ワ附顐?%s\n", filename);
        return 1;
    }
    
    // 閺夆晜鐟╅崳椋庘偓鍦仧楠炲洭寮崶锔筋偨閻熸瑱缍侀崳鎾焻閺勫繒甯?
    
    // 闁稿繑濞婂Λ鎾棘閸ワ附顐?
    fclose(file);
    
    if (options->verbose) {
        printf("闁哄倸娲ｅ▎銏ゅ箥瑜戦、鎴犫偓鐟版湰閸ㄦ瓡n");
    }
    
    return 0;
}

/**
 * 闁汇垻鍠愰崹姘舵煂韫囨挾鎽嶉柛?
 */
int generate_quantum_field(const char* output_file, const CommandOptions* options) {
    if (options->verbose) {
        printf("闁汇垻鍠愰崹姘舵煂韫囨挾鎽嶉柛锕€鎼懟鐔哥┍濠靛棛鎽犻柛? %s\n", output_file);
    }
    
    // 闁告帗绋戠紓鎾寸▔閳ь剚绋夐鍫濇閻庢稒鍔曞┃鈧?
    QField* field = quantum_field_create("generated_field", QFIELD_CONSCIOUSNESS);
    if (!field) {
        fprintf(stderr, "闂佹寧鐟ㄩ銈夋晬濮橆剙鐏＄€点倖妞介崳铏光偓娑欏姇濠р偓濠㈡儼绮剧憴顩俷");
        return 1;
    }
    
    // 婵烇綀顕ф慨鐐寸▔閳ь剚绂嶅☉婊兾濋柣?
    for (int i = 0; i < 10; i++) {
        QFieldNode node;
        node.x = (double)rand() / RAND_MAX * 10.0 - 5.0;
        node.y = (double)rand() / RAND_MAX * 10.0 - 5.0;
        node.z = (double)rand() / RAND_MAX * 10.0 - 5.0;
        node.intensity = (double)rand() / RAND_MAX;
        node.state = NULL;
        
        quantum_field_add_node(field, &node);
    }
    
    // 闁告瑯鍨甸～瀣礌閺嵮勭皻
    int result = quantum_field_visualize(field, output_file);
    
    // 闂佹彃锕ラ弬浣烘導閸曨剛鐖?
    quantum_field_destroy(field);
    
    if (result != 0) {
        fprintf(stderr, "闂佹寧鐟ㄩ銈夋晬濮橆剙璁查悷娆忔鐎垫煡鏌岃箛鎾舵憤闁革箑鎼妵鎴犳嫻椤ь晹");
        return 1;
    }
    
    if (options->verbose) {
        printf("闂佹彃绻愰悺娆撳捶閸濆嫬鍤掗柣銏㈠枑閸ㄦ岸鐛張鐢电閻庢稒顩硁");
    }
    
    return 0;
}

/**
 * 閺夆晜鍔橀、鎴澝圭€ｎ厾妲?
 */
int run_test(const char* test_file) {
    printf("閺夆晜鍔橀、鎴澝圭€ｎ厾妲?);
    if (test_file && test_file[0] != '\0') {
        printf(": %s", test_file);
    }
    printf("\n");
    
    // 闁革负鍔忕换鏍煂鐏炵晫鏉介柣婊呭缁佸鎷犻弴鈶╁亾閺勫繒甯?
    if (test_file && test_file[0] != '\0') {
        // 閺夆晜鍔橀、鎴︽偋閻熸壆鏆版繛鏉戭儓閻?
        if (strcmp(test_file, "quantum_state") == 0) {
            // 閺夆晜鍔橀、鎴︽煂韫囨挾鎽嶉柣妯垮煐閳ь兛鐒︾粊瀵告嫚?
            printf("閺夆晜鍔橀、鎴︽煂韫囨挾鎽嶉柣妯垮煐閳ь兛鐒︾粊瀵告嫚?..\n");
            // 閺夆晜鐟╅崳鐑芥閳ь剛鎲版担鐣屾闁活潿鍔嶇粊瀵告嫚閺囩偛姣愰柡?
            return 0;
        } else if (strcmp(test_file, "quantum_entanglement") == 0) {
            // 閺夆晜鍔橀、鎴︽煂韫囨挾鎽嶇紒鍓уХ缁辫泛霉鐎ｎ厾妲?
            printf("閺夆晜鍔橀、鎴︽煂韫囨挾鎽嶇紒鍓уХ缁辫泛霉鐎ｎ厾妲?..\n");
            // 閺夆晜鐟╅崳鐑芥閳ь剛鎲版担鐣屾闁活潿鍔嶇粊瀵告嫚閺囩偛姣愰柡?
            return 0;
        } else if (strcmp(test_file, "quantum_field") == 0) {
            // 閺夆晜鍔橀、鎴︽煂韫囨挾鎽嶉柛锔惧劋缁佸鎷?
            printf("閺夆晜鍔橀、鎴︽煂韫囨挾鎽嶉柛锔惧劋缁佸鎷?..\n");
            // 閺夆晜鐟╅崳鐑芥閳ь剛鎲版担鐣屾闁活潿鍔嶇粊瀵告嫚閺囩偛姣愰柡?
            return 0;
        } else if (strcmp(test_file, "quantum_gene") == 0) {
            // 閺夆晜鍔橀、鎴︽煂韫囨挾鎽嶉柛鈺佹惈濞叉粌霉鐎ｎ厾妲?
            printf("閺夆晜鍔橀、鎴︽煂韫囨挾鎽嶉柛鈺佹惈濞叉粌霉鐎ｎ厾妲?..\n");
            // 閺夆晜鐟╅崳鐑芥閳ь剛鎲版担鐣屾闁活潿鍔嶇粊瀵告嫚閺囩偛姣愰柡?
            return 0;
        } else {
            fprintf(stderr, "闂佹寧鐟ㄩ銈夋晬濮橆厽寮撻柣顓滃劜缁佸鎷?%s\n", test_file);
            return 1;
        }
    } else {
        // 閺夆晜鍔橀、鎴﹀箥閳ь剟寮垫径瀣偞閻?
        printf("閺夆晜鍔橀、鎴﹀箥閳ь剟寮垫径瀣偞閻?..\n");
        // 閺夆晜鐟╅崳鐑芥閳ь剛鎲版担鐣屾闁活潿鍔岄崣蹇涙焾閵婏妇銈撮悹鍥ㄦ礀閸ら亶寮?
        return 0;
    }
} 
