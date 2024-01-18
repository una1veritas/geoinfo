// Dikstras.cpp : このファイルには 'main' 関数が含まれています。プログラム実行の開始と終了がそこで行われます。
//
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <queue>
#include <algorithm>
#include <limits>
#include <cmath>
#include <cinttypes>

typedef int64_t int64;

using namespace std;

struct DataEntry {
    double lat, lon;  // 緯度と経度
    vector<int64> adj;   // 隣接リスト

    // デフォルトコンストラクタを追加し、メンバー変数を初期化
    DataEntry() : lat(0.0), lon(0.0), adj() {}
    DataEntry(const double & lati, const double & longi, const std::vector<int64> & adjlist) : lat(lati), lon(longi), adj(adjlist.cbegin(), adjlist.cend()) {}
};

// 地球の半径（メートル）
constexpr double EARTH_RADIUS = 6371000.0;

// ラジアンを度に変換
double toRadians(double degree) {
    //const double M_PI = 3.141592653589793;
    return degree * M_PI / 180.0;
}

// 2点間の距離を計算する関数（地球の丸みを考慮）
double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
    // 緯度経度をラジアンに変換
    double radLat1 = toRadians(lat1);
    double radLon1 = toRadians(lon1);
    double radLat2 = toRadians(lat2);
    double radLon2 = toRadians(lon2);

    // ハーフバーシンの公式を用いて距離を計算
    double dLat = radLat2 - radLat1;
    double dLon = radLon2 - radLon1;
    double a = sin(dLat / 2.0) * sin(dLat / 2.0) + cos(radLat1) * cos(radLat2) * sin(dLon / 2.0) * sin(dLon / 2.0);
    double c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a));

    // 距離をメートル単位で返す
    return EARTH_RADIUS * c;
}

// ダイクストラ法で最短距離と経路を求める関数
pair<vector<int64>, unordered_map<int64, double>> dijkstra(const unordered_map<int64, DataEntry>& graph, int64 start, int64 goal) {
    // 優先度付きキューを使って最短距離を管理する
    priority_queue<pair<double, int64>, vector<pair<double, int64>>, greater<pair<double, int64>>> pq;
    // 各ノードまでの最短距離を保存するマップ
    unordered_map<int64, double> dist;
    // 各ノードの直前のノードを保存するマップ
    unordered_map<int64, int64> prev;

    // 各ノードの最短距離を無限大、直前のノードを未定義に初期化
    for (const auto& entry : graph) {
        dist[entry.first] = numeric_limits<double>::infinity();
        prev[entry.first] = entry.first;
    }

    // 始点の最短距離を0に設定してキューに追加
    dist[start] = 0.0;
    pq.push({ 0.0, start });

    // ダイクストラ法のメインループ
    while (!pq.empty()) {
        double current_dist = pq.top().first;
        int current_node = pq.top().second;
        pq.pop();

        // ゴールノードに到達したら終了
        if (current_node == goal) {
            break;
        }

        // キューから取り出したノードが未定義の場合は無視
        if (graph.find(current_node) == graph.end()) {
            continue;
        }

        // キューから取り出したノードの最短距離が既知の最短距離よりも大きい場合は無視
        if (current_dist > dist[current_node]) {
            continue;
        }

        // 隣接するノードに対して最短距離を更新し、キューに追加
        for (int neighbor : graph.at(current_node).adj) {
            // グラフ内にノードが存在しない場合は無視
            if (graph.find(neighbor) == graph.end()) {
                continue;
            }

            // 2点間の距離を計算
            double cost = calculateDistance(graph.at(current_node).lat, graph.at(current_node).lon,
                graph.at(neighbor).lat, graph.at(neighbor).lon);

            // 最短距離が更新される場合は、最短距離と直前のノードを更新し、キューに追加
            if (dist[current_node] + cost < dist[neighbor]) {
                dist[neighbor] = dist[current_node] + cost;
                prev[neighbor] = current_node;
                pq.push({ dist[neighbor], neighbor });
            }
        }
    }

    // ゴールノードまでの最短経路を復元
    vector<int64> path;
    int64 current = goal;
    while (current != start && prev[current] != current) {
        path.push_back(current);
        current = prev[current];
    }
    reverse(path.begin(), path.end());

    // 最短経路と最短距離を返す
    return { path, dist };
}


// readData関数
unordered_map<int64, DataEntry> readData(const string& filename, char delimiter) {
    unordered_map<int64, DataEntry> data;
    cout << "reading '" << filename << "'..." << endl << flush;
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "ファイルが開けませんでした: " << filename << endl;
        return data; // 空のマップを返す
    }

    string line;
    //unsigned int linenum = 0;
    while (getline(file, line)) {
    	//cout << ++linenum << ": " << line << endl << std::flush;
        stringstream ss(line);
        int64 id, t;
        string tstr;
        std::vector<int64> adjs;

        getline(ss, tstr, delimiter);
        id = stoll(tstr);
        //cout << t << ", ";

        getline(ss, tstr, delimiter);
        double lat = stod(tstr);
        //cout << lat << ", ";

        getline(ss, tstr, delimiter);
        double lon = stod(tstr);
        //cout << lon << "; ";

        while (getline(ss, tstr, delimiter)) {
        	t = stoll(tstr);
        	adjs.push_back(t);
        	//cout << t << ", ";
        }

        data[id] = DataEntry(lat, lon, adjs);
        //cout << endl << flush;
    }

    file.close();
    cout << endl;
    return data;
}

int main(int argc, char * argv[]) {
	cout << "sizeof(int) = " << sizeof(int) << endl;
	cout << "sizeof(long) = " << sizeof(long) << endl;
	cout << "sizeof(int64) = " << sizeof(int64) << endl;

    if ( ! (argc > 1) ) {
    	cout << "file name is required." << endl;
    	exit(1);
    }
    string filename = string(argv[1]);
    char delimiter = ',';
    unordered_map<int64, DataEntry> graph = readData(filename, delimiter); //ここで実行エラーが起きる
    if ( graph.size() == 0 ) {
    	exit(1);
    }
    cout << "Graph nodes = " << graph.size() << " points." << endl;
    
    // 確認用の表示
    cout << "Graph Contents:" << endl;
    int c = 0;
    for (const auto& entry : graph) {
    	++c;
        cout << "ID: " << entry.first << " ";
        cout << "Lat: " << entry.second.lat << " ";
        cout << "Lon: " << entry.second.lon << " ";
        cout << "Adj: ";
        for (const auto& adj : entry.second.adj) {
            cout << adj << " ";
        }
        cout << endl;
        if ( c > 16 ) {
        	cout << "..." << endl;
        	break;
        }
    }
    cout << "------------------" << endl;
    
    
    int64 startNode = 10019851356; //265880475;  // スタートノードのID
    int64 goalNode = 10019827088; //265880486;   // ゴールノードのID

    auto result = dijkstra(graph, startNode, goalNode);
    vector<int64> shortestPath = result.first;
    unordered_map<int64, double> shortestDistances = result.second;

    cout << "最短経路: ";
    for (int64 node : shortestPath) {
        cout << node << " ";
    }
    cout << endl;

    cout << "最短距離: " << shortestDistances[goalNode] << " メートル" << endl;

    // SDLウィンドウに地図と最短経路を描画
    //show_in_sdl_window(graph, shortestPath);
    
    return 0;
}






// プログラムの実行: Ctrl + F5 または [デバッグ] > [デバッグなしで開始] メニュー
// プログラムのデバッグ: F5 または [デバッグ] > [デバッグの開始] メニュー

// 作業を開始するためのヒント: 
//    1. ソリューション エクスプローラー ウィンドウを使用してファイルを追加/管理します 
//   2. チーム エクスプローラー ウィンドウを使用してソース管理に接続します
//   3. 出力ウィンドウを使用して、ビルド出力とその他のメッセージを表示します
//   4. エラー一覧ウィンドウを使用してエラーを表示します
//   5. [プロジェクト] > [新しい項目の追加] と移動して新しいコード ファイルを作成するか、[プロジェクト] > [既存の項目の追加] と移動して既存のコード ファイルをプロジェクトに追加します
//   6. 後ほどこのプロジェクトを再び開く場合、[ファイル] > [開く] > [プロジェクト] と移動して .sln ファイルを選択します
