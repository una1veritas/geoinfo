#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <queue>
#include <limits>
#include <cmath>
#include <algorithm>
#include <random>  // ランダムなノードを選ぶために追加
#include <chrono>
#include <unordered_set>
//#include <SDL.h>

using namespace std;

// DataEntry 構造体
struct DataEntry {
    double lat, lon;  // 緯度と経度
    vector<long long> adj;   // 隣接リスト

    // デフォルトコンストラクタを追加し、メンバー変数を初期化
    DataEntry() : lat(0.0), lon(0.0) {}
};

// 地球の半径（メートル）
constexpr double EARTH_RADIUS = 6371000.0;

// 既に定義されている場合は再定義しないようにする
#ifndef M_PI
const double M_PI = 3.141592653589793;
#endif

// ラジアンを度に変換
double toRadians(double degree) {
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

// パスの距離を計算する関数
double calculatePathDistance(const unordered_map<long long, DataEntry>& graph, const vector<long long>& path) {
    double totalDistance = 0.0;

    // パスを反復処理し、距離を累積する
    for (size_t i = 0; i < path.size() - 1; ++i) {
        long long currentID = path[i];
        long long nextID = path[i + 1];

        // ノードがグラフに存在するか確認
        if (graph.find(currentID) != graph.end() && graph.find(nextID) != graph.end()) {
            // 連続するノード間の距離を計算
            double distance = calculateDistance(graph.at(currentID).lat, graph.at(currentID).lon,
                graph.at(nextID).lat, graph.at(nextID).lon);
            totalDistance += distance;
        }
        else {
            cout << "エラー: パス内の1つ以上のノードがグラフ内に存在しません。" << endl;
            return -1.0;  // エラー値を返す
        }
    }

    return totalDistance;
}

// 安全地帯内のノードを求める関数（vecter型のノードの集合を返り値にするバージョン）
vector<long long> findNodesInZone(const unordered_map<long long, DataEntry>& graph, long long center, double radius) {
    vector<long long> nodes_in_zone;

    for (const auto& entry : graph) {
        double distance = calculateDistance(graph.at(center).lat, graph.at(center).lon, entry.second.lat, entry.second.lon);
        if (distance <= radius) {
            nodes_in_zone.push_back(entry.first);
        }
    }

    return nodes_in_zone;
}

bool isIdInSet(long long targetId, const vector<long long>& idSet) {
    auto it = find(idSet.begin(), idSet.end(), targetId);
    return it != idSet.end();
}

void checkMovementRequired(long long currentID, const vector<long long>& safeZoneIDs) {
    // 集合に含まれているかどうかを確認
    auto it = find(safeZoneIDs.begin(), safeZoneIDs.end(), currentID);

    // メッセージを出力
    if (it != safeZoneIDs.end()) {
        cout << "○移動は不要: 現在地は次の安全地帯の中であるので移動しなくてよい。" << endl;
    }
    else {
        cout << "○移動が必要: 現在地は次の安全地帯の外であるので移動しなければならない。" << endl;
    }
}

// 最短経路と最短距離を出力する関数（ID:265880475(33.6937, 130.712)の形式で表示）
void printShortestPathAndDistance(const vector<long long>& path, const unordered_map<long long, DataEntry>& graph) {
    if (path.empty()) {
        cout << "最短経路が計算できませんでした。" << endl;
        return;
    }

    double shortestDistance = 0.0;

    cout << "○最短経路: ";
    for (size_t i = 0; i < path.size(); ++i) {
        long long node = path[i];
        cout << "ID:" << node << "(" << graph.at(node).lat << ", " << graph.at(node).lon << ") ";

        if (i > 0) {
            // スタートノードからゾーン内への最短距離になるノードにおけるパスの距離を求める
            double cost = calculateDistance(graph.at(path[i - 1]).lat, graph.at(path[i - 1]).lon,
                graph.at(node).lat, graph.at(node).lon);
            shortestDistance += cost;
        }
    }
    cout << endl;

    cout << "○最短距離: " << shortestDistance << " メートル" << endl;
}

void dijkstraToZone(
    const unordered_map<long long, DataEntry>& graph,
    long long& start, 
    const vector<long long>& nodes_inside_the_zone) {

    // 各ノードまでの最短距離を保存するマップ
    unordered_map<long long, double> dist;
    // 各ノードの直前のノードを保存するマップ
    unordered_map<long long, long long> prev;
    // プロセスしたノードのセット
    unordered_set<long long> processed;

    // 各ノードの最短距離を無限大、直前のノードを未定義に初期化
    for (const auto& entry : graph) {
        dist[entry.first] = numeric_limits<double>::infinity();
        prev[entry.first] = -1;
    }

    // 始点の最短距離を0に設定
    dist[start] = 0.0;

    // ダイクストラ法のメインループ
    while (true) {
        // 未処理のノードの中で最短距離のノードを見つける
        long long current_node = -1;
        double min_dist = numeric_limits<double>::infinity();

        for (const auto& entry : graph) {
            long long node = entry.first;
            if (processed.find(node) == processed.end() && dist[node] < min_dist) {
                min_dist = dist[node];
                current_node = node;
            }
        }

        // 未処理のノードがなくなったら終了
        if (current_node == -1) {
        	cout << "current_node == -1" << endl;
            break;
        }

        // ノードを処理済みとしてマーク
        processed.insert(current_node);

        // nodes_inside_the_zone 内のノードに到達したら終了
        if (find(nodes_inside_the_zone.begin(), nodes_inside_the_zone.end(), current_node) != nodes_inside_the_zone.end()) {
            // nodes_inside_the_zone までの最短経路を復元
            vector<long long> path;
            long long current = current_node;

            while (current != -1) {
                path.push_back(current);
                current = prev[current];
            }
            reverse(path.begin(), path.end());

            cout << path.size() << endl;
            // 最短経路と最短距離を出力する
           //printShortestPathAndDistance(path, graph);

            // 最短経路の最後の地点を start に設定
            start = path.back();

            // 処理終了
            return;
        }

        // 隣接するノードに対して最短距離を更新
        for (long long neighbor : graph.at(current_node).adj) {
            // グラフ内にノードが存在しない場合は無視
            if (graph.find(neighbor) == graph.end()) {
                continue;
            }

            // 2点間の距離を計算
            double cost = calculateDistance(graph.at(current_node).lat, graph.at(current_node).lon,
                graph.at(neighbor).lat, graph.at(neighbor).lon);

            // 最短距離が更新される場合は、最短距離と直前のノードを更新
            if (dist[current_node] + cost < dist[neighbor]) {
                dist[neighbor] = dist[current_node] + cost;
                prev[neighbor] = current_node;
            }
        }
    }

    // ゴールが見つからなかった場合のエラーメッセージ
    cout << "Error: nodes_inside_the_zone までの最短経路が見つかりませんでしたので、キャラクターの特殊能力やアイテムを使って次の安全地帯内へ強引に入ってください" << endl;
}


// 優先順位付きキューを用いたダイクストラ法で最短距離と経路を求める関数 O((V + E) * log V) 
void dijkstraToZone_pq(
    const unordered_map<long long, DataEntry>& graph,
    long long& start, 
    const vector<long long>& nodes_inside_the_zone) {

    // 優先度付きキューを使って最短距離を管理する
    priority_queue<pair<double, long long>, vector<pair<double, long long>>, greater<pair<double, long long>>> pq;
    // 各ノードまでの最短距離を保存するマップ
    unordered_map<long long, double> dist;
    // 各ノードの直前のノードを保存するマップ
    unordered_map<long long, long long> prev;

    // 各ノードの最短距離を無限大、直前のノードを未定義に初期化
    for (const auto& entry : graph) {
        dist[entry.first] = numeric_limits<double>::infinity();
        prev[entry.first] = -1;
    }

    // 始点の最短距離を0に設定してキューに追加
    dist[start] = 0.0;
    pq.push({ 0.0, start });

    // ダイクストラ法のメインループ
    while (!pq.empty()) {
        double current_dist = pq.top().first;
        long long current_node = pq.top().second;
        pq.pop();

        // キューから取り出したノードの最短距離が既知の最短距離よりも大きい場合は無視
        if (current_dist > dist[current_node]) {
            continue;
        }

        // nodes_inside_the_zone 内のノードに到達したら終了
        if (find(nodes_inside_the_zone.begin(), nodes_inside_the_zone.end(), current_node) != nodes_inside_the_zone.end()) {
            // nodes_inside_the_zone までの最短経路を復元
            vector<long long> path;
            long long current = current_node;

            while (current != -1) {
                path.push_back(current);
                current = prev[current];
            }
            reverse(path.begin(), path.end());

            // 最短経路と最短距離を出力する
            printShortestPathAndDistance(path, graph);

            // 最短経路の最後の地点を start に設定
            start = path.back();

            // 処理終了
            return;
        }

        // 隣接するノードに対して最短距離を更新し、キューに追加
        for (long long neighbor : graph.at(current_node).adj) {
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

    // ゴールが見つからなかった場合のエラーメッセージ
    cout << "Error: nodes_inside_the_zone までの最短経路が見つかりませんでしたので、キャラクターの特殊能力やアイテムを使って次の安全地帯内へ強引に入ってください。" << endl;
}



/*
// 新しい安全地帯の中心を求める関数
long long determineNextSafeZoneCenter(
    unordered_map<long long, DataEntry>& graph,
    vector<long long>& nodes_in_new_zone,
    double original_zone_radius,
    double new_zone_radius) {

    // 1. ランダムなノードを選ぶための乱数エンジンを初期化
    random_device rd;
    mt19937 gen(rd());

    // 2. 新しい安全地帯内の全てのノードが元のグラフ内に含まれている中心のIDを格納するベクトル
    vector<long long> candidate_centers;

    // 3. グラフ内の各ノードに対して処理を行うループ
    for (const auto& entry : graph) {
        // 4. 各ノードを中心として新しい安全地帯内のノードを求める
        nodes_in_new_zone.clear();  // 新しいデータを格納する前にクリア
        nodes_in_new_zone = findNodesInZone(graph, entry.first, new_zone_radius);

        // 5. 新しい安全地帯内の全てのノードが元のグラフ内に含まれているかつ新しい円の中に収まっている場合
        bool all_nodes_inside = true;
        for (long long node : nodes_in_new_zone) {
            if (graph.find(node) == graph.end()) {
                all_nodes_inside = false;
                break;
            }
        }

        // 新しい円の中に収まっているかどうかの判断を追加
        double distance_to_center = calculateDistance(graph.at(entry.first).lat, graph.at(entry.first).lon, entry.second.lat, entry.second.lon);
        if (all_nodes_inside && distance_to_center + new_zone_radius <= original_zone_radius) {
            candidate_centers.push_back(entry.first);
        }
    }

    // 6. 中心が見つからなかった場合はエラーメッセージを表示して -1 を返す
    if (candidate_centers.empty()) {
        cout << "Error: 新しい安全地帯の中心が見つかりませんでした。条件を確認してください。" << endl;
        return -1;
    }

    // 7. ランダムにノードを選んで返す
    uniform_int_distribution<long long> distribution(0, candidate_centers.size() - 1);
    long long random_center_index = distribution(gen);
    return candidate_centers[random_center_index];
}
*/



// readData関数
unordered_map<long long, DataEntry> readData(const string& filename, char delimiter) {
    unordered_map<long long, DataEntry> data;

    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "ファイルが開けませんでした: " << filename << endl;
        return data; // 空のマップを返す
    }

    string line;
    while (getline(file, line)) {
        stringstream ss(line);
        DataEntry entry;

        string id_str;
        getline(ss, id_str, delimiter);
        long long id = stoll(id_str);

        string lat_str;
        getline(ss, lat_str, delimiter);
        entry.lat = stod(lat_str);

        string lon_str;
        getline(ss, lon_str, delimiter);
        entry.lon = stod(lon_str);

        string adj_str;
        while (getline(ss, adj_str, delimiter)) {
            entry.adj.push_back(stoll(adj_str));
        }

        data[id] = entry;
    }

    file.close();
    return data;
}




int main() {
    string filename = "map-iizuka.geo";
    char delimiter = ',';
    unordered_map<long long, DataEntry> graph = readData(filename, delimiter);

    // 確認用コード
    /*
    cout << "Graph Contents:" << endl;
    for (const auto& entry : graph) {
        cout << "ID: " << entry.first << " ";
        cout << "Lat: " << entry.second.lat << " ";
        cout << "Lon: " << entry.second.lon << " ";
        cout << "Adj: ";
        for (const auto& adj : entry.second.adj) {
            cout << adj << " ";
        }
        cout << endl;
    }
    cout << "------------------" << endl;*/
    
    // 確認用コード
    /*
    // 例としてのパス
    vector<long long> examplePath = {5298668495, 5298668494, 265880506, 5341879237, 5341879235, 1385515450};

    // パスの距離を計算して表示
    double pathDistance = calculatePathDistance(graph, examplePath);

    if (pathDistance >= 0.0) {
        cout << "与えられたパスの総距離: " << pathDistance << " メートル" << endl;
    }*/
    
    cout << "ラウンド1" << endl;

    long long startNode = 5913224194;
    // 5913224194,33.6368978,130.6726952 map-iizuka.geoの穂波イオンの花屋さん
    // 6026258053,33.6441972,130.6938716 map-iizuka.geoの新飯塚駅前の入口
    // 5913224194,33.6368978,130.6726952 map-iizuka-central.geoの穂波イオンの花屋さん
    // 6026258053,33.6441972,130.6938716 map-iizuka-central.geoの新飯塚駅前の入口

    // スタートノードのIDに対応する緯度と経度を取得
    double startLat, startLon;

    // 現在地の出力の準備
    if (graph.find(startNode) != graph.end()) {
        startLat = graph[startNode].lat;
        startLon = graph[startNode].lon;
    }
    else {
        cout << "Error: 指定されたIDのノードが見つかりません。" << endl;
        return 1;  // エラーコードを返してプログラムを終了
    }
    // 現在地を指定された形式で出力
    cout << "現在地  ID:" << startNode << "(" << startLat << ", " << startLon << ")" << endl;

    // graphのキーである全てのIDを取得し、vector<long long>型の変数に格納
    vector<long long> nodes_inside_the_current_zone;
    for (const auto& entry : graph) {
        nodes_inside_the_current_zone.push_back(entry.first);
    }

    // 次の安全地帯の中心と半径
    long long center_of_next_zone = 1540568884; // 九工大のKITの植物アートのところ
    double next_zone_radius = 500.0;

    // 1回目の実行時間計測
    auto start_time_1 = chrono::high_resolution_clock::now();

    // 次の安全地帯内のノードを求める
    vector<long long> nodes_inside_the_next_zone = findNodesInZone(graph, center_of_next_zone, next_zone_radius);

    // 現在地の状態の出力
    checkMovementRequired(startNode, nodes_inside_the_next_zone);

    dijkstraToZone_pq(graph, startNode, nodes_inside_the_next_zone);

    // nodes_inside_the_current_zoneにnodes_inside_the_next_zoneを代入
    nodes_inside_the_current_zone = nodes_inside_the_next_zone;

    // graph内のIDについて、nodes_inside_the_current_zoneに入っているIDだけを残す
    unordered_map<long long, DataEntry> current_graph;
    for (long long id : nodes_inside_the_current_zone) {
        auto it = graph.find(id);
        if (it != graph.end()) {
            current_graph[id] = it->second;
        }
    }

    // 処理1
    auto end_time_1 = chrono::high_resolution_clock::now();
    auto duration_1 = chrono::duration_cast<chrono::milliseconds>(end_time_1 - start_time_1);
    cout << "実行時間 1: " << duration_1.count() << " ミリ秒" << endl;

    // 改行を出力
    cout << endl;

    cout << "◎ラウンド2" << endl;

    // 現在地の出力の準備
    if (graph.find(startNode) != graph.end()) {
        startLat = graph[startNode].lat;
        startLon = graph[startNode].lon;
    }
    else {
        cout << "Error: 指定されたIDのノードが見つかりません。" << endl;
        return 1;  // エラーコードを返してプログラムを終了
    }
    // 現在地を指定された形式で出力
    cout << "○現在地  ID:" << startNode << "(" << startLat << ", " << startLon << ")" << endl;

    // 半径を指定する
    next_zone_radius = 250.0;
    // center_of_next_zone = 1540568884; // 九工大のKITの植物アートのところ

    // 2回目の実行時間計測
    auto start_time_2 = chrono::high_resolution_clock::now();

    // 新しい安全地帯内のノードを求める
    nodes_inside_the_next_zone = findNodesInZone(graph, center_of_next_zone, next_zone_radius);

    // 確認用
    bool result = isIdInSet(center_of_next_zone, nodes_inside_the_next_zone);

    if (result) {
        cout << "○ID " << center_of_next_zone << " は集合に含まれています。" << endl;
    }
    else {
        cout << "○ID " << center_of_next_zone << " は集合に含まれていません。" << endl;
    }

    // 次の安全地帯の中心の情報の出力
    if (center_of_next_zone != -1 && current_graph.find(center_of_next_zone) != current_graph.end()) {
        cout << "○次の安全地帯の中心　ID:" << center_of_next_zone << "("
            << current_graph[center_of_next_zone].lat << ", " << current_graph[center_of_next_zone].lon << ")"
            << endl;
    }

    // 現在地の状態の出力
    checkMovementRequired(startNode, nodes_inside_the_next_zone);

    // nodes_inside_the_current_zoneの中身を出力
    cout << "○現在の安全地帯内のノード: ";
    for (long long node : nodes_inside_the_current_zone) {
        cout << "ID:" << node << "(" << graph[node].lat << ", " << graph[node].lon << ") ";
    }
    cout << endl;

    // nodes_inside_the_next_zoneの中身を出力
    cout << "○次の安全地帯内のノード: ";
    for (long long node : nodes_inside_the_next_zone) {
        cout << "ID:" << node << "(" << graph[node].lat << ", " << graph[node].lon << ") ";
    }
    cout << endl;

    dijkstraToZone_pq(current_graph, startNode, nodes_inside_the_next_zone);

    // nodes_inside_the_current_zoneにnodes_inside_the_next_zoneを代入
    nodes_inside_the_current_zone = nodes_inside_the_next_zone;

    // graph内のIDについて、nodes_inside_the_current_zoneに入っているIDだけを残す
    for (long long id : nodes_inside_the_current_zone) {
        auto it = graph.find(id);
        if (it != graph.end()) {
            current_graph[id] = it->second;
        }
    }

    auto end_time_2 = chrono::high_resolution_clock::now();
    auto duration_2 = chrono::duration_cast<chrono::milliseconds>(end_time_2 - start_time_2);
    cout << "実行時間 2: " << duration_2.count() << " ミリ秒" << endl;

    // 改行を出力
    cout << endl;

    cout << "◎ラウンド3" << endl;

    // 現在地の出力の準備
    if (graph.find(startNode) != graph.end()) {
        startLat = graph[startNode].lat;
        startLon = graph[startNode].lon;
    }
    else {
        cout << "Error: 指定されたIDのノードが見つかりません。" << endl;
        return 1;  // エラーコードを返してプログラムを終了
    }
    // 現在地を指定された形式で出力
    cout << "○現在地  ID:" << startNode << "(" << startLat << ", " << startLon << ")" << endl;

    // 半径を指定
    next_zone_radius = 100.0;
    // center_of_next_zone = 1540568884; // 九工大のKITの植物アートのところ
    
    // 3回目の実行時間計測
    auto start_time_3 = chrono::high_resolution_clock::now();

    // 次の安全地帯内のノードを求める
    nodes_inside_the_next_zone = findNodesInZone(graph, center_of_next_zone, next_zone_radius);

    // 確認用
    result = isIdInSet(center_of_next_zone, nodes_inside_the_next_zone);

    if (result) {
        cout << "○ID " << center_of_next_zone << " は集合に含まれています。" << endl;
    }
    else {
        cout << "○ID " << center_of_next_zone << " は集合に含まれていません。" << endl;
    }

    // nodes_inside_the_current_zoneの中身を出力
    cout << "○現在の安全地帯内のノード: ";
    for (long long node : nodes_inside_the_current_zone) {
        cout << "ID:" << node << "(" << graph[node].lat << ", " << graph[node].lon << ") ";
    }
    cout << endl;

    // 次の安全地帯の中心の情報の出力
    if (center_of_next_zone != -1 && current_graph.find(center_of_next_zone) != current_graph.end()) {
        cout << "○次の安全地帯の中心　ID:" << center_of_next_zone << "("
            << current_graph[center_of_next_zone].lat << ", " << current_graph[center_of_next_zone].lon << ")"
            << endl;
    }

    // 現在地の状態の出力
    checkMovementRequired(startNode, nodes_inside_the_next_zone);

    // nodes_inside_the_next_zoneの中身を出力
    cout << "○次の安全地帯内のノード: ";
    for (long long node : nodes_inside_the_next_zone) {
        cout << "ID:" << node << "(" << graph[node].lat << ", " << graph[node].lon << ") ";
    }
    cout << endl;

    dijkstraToZone_pq(current_graph, startNode, nodes_inside_the_next_zone);

    // nodes_inside_the_current_zoneにnodes_inside_the_next_zoneを代入
    nodes_inside_the_current_zone = nodes_inside_the_next_zone;

    // graph内のIDについて、nodes_inside_the_current_zoneに入っているIDだけを残す
    for (long long id : nodes_inside_the_current_zone) {
        auto it = graph.find(id);
        if (it != graph.end()) {
            current_graph[id] = it->second;
        }
    }

    auto end_time_3 = chrono::high_resolution_clock::now();
    auto duration_3 = chrono::duration_cast<chrono::milliseconds>(end_time_3 - start_time_3);
    cout << "実行時間 3: " << duration_3.count() << " ミリ秒" << endl;

    // 改行を出力
    cout << endl;
    
    cout << "◎ラウンド4" << endl;

    // 現在地の出力の準備
    if (graph.find(startNode) != graph.end()) {
        startLat = graph[startNode].lat;
        startLon = graph[startNode].lon;
    }
    else {
        cout << "Error: 指定されたIDのノードが見つかりません。" << endl;
        return 1;  // エラーコードを返してプログラムを終了
    }
    // 現在地を指定された形式で出力
    cout << "○現在地  ID:" << startNode << "(" << startLat << ", " << startLon << ")" << endl;

    // 半径を指定
    next_zone_radius = 0.0;
    // center_of_next_zone = 1540568884; // 九工大のKITの植物アートのところ
    
    // 4回目の実行時間計測
    auto start_time_4 = chrono::high_resolution_clock::now();
    
    // 次の安全地帯内のノードを求める
    nodes_inside_the_next_zone = findNodesInZone(graph, center_of_next_zone, next_zone_radius);

    // 確認用
    result = isIdInSet(center_of_next_zone, nodes_inside_the_next_zone);

    if (result) {
        cout << "○ID " << center_of_next_zone << " は集合に含まれています。" << endl;
    }
    else {
        cout << "○ID " << center_of_next_zone << " は集合に含まれていません。" << endl;
    }

    // 次の安全地帯の中心の情報の出力
    if (center_of_next_zone != -1 && current_graph.find(center_of_next_zone) != current_graph.end()) {
        cout << "○次の安全地帯の中心　ID:" << center_of_next_zone << "("
            << current_graph[center_of_next_zone].lat << ", " << current_graph[center_of_next_zone].lon << ")"
            << endl;
    }

    // 現在地の状態の出力
    checkMovementRequired(startNode, nodes_inside_the_next_zone);

    // nodes_inside_the_current_zoneの中身を出力
    cout << "○現在の安全地帯内のノード: ";
    for (long long node : nodes_inside_the_current_zone) {
        cout << "ID:" << node << "(" << graph[node].lat << ", " << graph[node].lon << ") ";
    }
    cout << endl;

    // nodes_inside_the_next_zoneの中身を出力
    cout << "○次の安全地帯内のノード: ";
    for (long long node : nodes_inside_the_next_zone) {
        cout << "ID:" << node << "(" << graph[node].lat << ", " << graph[node].lon << ") ";
    }
    cout << endl;

    dijkstraToZone_pq(current_graph, startNode, nodes_inside_the_next_zone);

    // nodes_inside_the_current_zoneにnodes_inside_the_next_zoneを代入
    nodes_inside_the_current_zone = nodes_inside_the_next_zone;

    // graph内のIDについて、nodes_inside_the_current_zoneに入っているIDだけを残す
    for (long long id : nodes_inside_the_current_zone) {
        auto it = graph.find(id);
        if (it != graph.end()) {
            current_graph[id] = it->second;
        }
    }

    auto end_time_4 = chrono::high_resolution_clock::now();
    auto duration_4 = chrono::duration_cast<chrono::milliseconds>(end_time_4 - start_time_4);
    cout << "実行時間 4: " << duration_4.count() << " ミリ秒" << endl;

    // 改行を出力
    cout << endl;
    
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
