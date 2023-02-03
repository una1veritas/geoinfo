#include<cstdio>
#include<iostream>
#include<set>
#include<fstream>
#include<map>
#include<vector>
#include <sstream>
#include <string>
#include <iomanip>
#include <stdio.h>

#include "geograph.h"
#include "bgeohash.h"
#include "geohash.h"


using namespace std;
#define NIL -1

//ノードのデータ構造を定義
struct GeoNode{
	bgeohash geohash; //ハッシュコード
	bool node_is_leaf ;
	int node;

	//葉ノードの場合
	set<geopoint> pset;

	//内部ノードの場合
	double mid;

	GeoNode *left,*right;

	//コンストラクタ
	GeoNode(bgeohash h , vector<geopoint> s){
		node_is_leaf = true;
		geohash = h;
		//pset = new set<geopoint>();
		for(const auto & p : s){
			pset.insert(p);
		}
		return;
	}

	GeoNode(bgeohash h, vector<geopoint> s, unsigned int limitprecision=0) {
		node_is_leaf = false;
		geohash = h;


		//if (h.precision() == limitprecision) {
		//精度が上限になった場合または、集合が範囲内にない場合、葉ノードを出力
		if (h.precision() >= limitprecision or s.size() == 0) {
			node_is_leaf = true;
			for (const auto &p : s) {
				pset.insert(p);
			}
			return;
		} else {
			/*for (const auto &p : s) {
				pset.insert(p);
			}*/
			// 分割するのは緯度か経度かの選択
			bool lat;
			bgeohash::coordbox box = geohash.decode();
			// geohash.precision() で判定する
			if ((geohash.precision() & 1) != 0) {
				//分割に使う緯度の値midを決定
				lat = true;
				mid = (box.n + box.s) / 2.0;
				//cout << "lon:" << box.e << "," << box.w;
			} else {
				//分割に使う経度の値midを決定
				lat = false;
				mid = (box.e + box.w) / 2.0;
			}
			vector<geopoint> lv, rv;

			//分割する緯度／経度と mid にしたがって、s を左の子の点列 lv と右の子の点列 rv にわける
			for (const auto &p : s) {
				if ((lat and (p.lat < mid)) or (!lat and (p.lon < mid))) {
					lv.push_back(p);
				} else {
					rv.push_back(p);
				}
			}

			if (lv.size() > 0) {
				bgeohash lhash(geohash);
				lhash.refine_bit(0);
				left = new GeoNode(lhash, lv, limitprecision);
			} else {
				left = NULL;
			}
			if (rv.size() > 0) {
				bgeohash rhash(geohash);
				rhash.refine_bit(1);
				right = new GeoNode(rhash, rv, limitprecision);
			} else {
				right = NULL;
			}
			// 分割に使う緯度または経度の値 mid の決定
			// 分割する緯度／経度と mid にしたがって、s を左の子の点列 lv と右の子の点列 rv にわける
			// geohash の精度を 1 あげて。最後のビットが 0 のハッシュ lhash と 1 の rhash を作る
			// lhash.precision() == 制度上限なら葉ノードを、そうでなければ内部ノード
			// left と right に new GeoNode(...) でそれぞれの子を作って割り当てる
			// left = new GeoNode(lhash, lv, 上限)
			// right = （略）
			return;
		}
	}

	bool is_leaf()const{
		return node_is_leaf;
	}

	vector<geopoint> search(bgeohash h) {
		GeoNode *node = this;
		//geohash = h;
		bgeohash::coordbox box = h.decode();
		vector<geopoint> a;
		std::vector<GeoNode*> path;
		GeoNode *prev;
		uint64_t intval = h.location();

		cout << h.decode() << endl;

		for (unsigned int i = 0; i < h.precision(); ++i) {
			if (node->is_leaf() == true ) {
				break;
			}
			if (((intval >> (63 - i)) & 1) == 0) {
				if (node->left == NULL) {
					break;
				} else {
					node = node->left;
					cout << node->geohash.decode() << endl;
				}
			} else {
				if (node->right == NULL) {
					break;
				} else {
					node = node->right;
					cout << node->geohash.decode() << endl;
				}
			}
		}


		path.push_back(node);
		prev = NULL;
		prev = path.back();

		//cout << box.covers(path.back()->pset) << endl;
		//cout << prev->geohash.decode() << endl;

		if (h.precision() == node->geohash.precision()) {
			while (path.empty() == false) {
				if (path.back()->is_leaf() == true) {
					for (const auto &gp : path.back()->pset) {
						a.push_back(gp);
						cout << "s2.size:";
						cout << a.size() << endl;
					}
					prev = path.back();
					cout << prev->geohash.decode() << endl;
					path.pop_back();
					cout << "戻る3" << endl;
					continue;
				} else if (path.back()->is_leaf() == false) {
					cout << "in_node" << endl;
					if (prev == path.back()->left) {
						cout << "a" << endl;
						if (path.back()->right == NULL) {
							prev = path.back();
							cout << prev->geohash.decode() << endl;
							path.pop_back();
							cout << "戻る1" << endl;
						} else {
							prev = path.back();
							cout << prev->geohash.decode() << endl;
							path.push_back(path.back()->right);
							cout << "right1" << endl;
						}
						continue;
					} else if (prev == path.back()->right) {

						cout << "b" << endl;
						prev = path.back();
						cout << prev->geohash.decode() << endl;
						path.pop_back();
						cout << "戻る2" << endl;
						continue;
					} else {
						cout << "c" << endl;
						if (path.back()->left == NULL) {
							prev = path.back();
							cout << prev->geohash.decode() << endl;
							path.push_back(path.back()->right);
							cout << "right2" << endl;

						} else {
							prev = path.back();
							cout << prev->geohash.decode() << endl;
							path.push_back(path.back()->left);
							cout << "left1" << endl;
						}

						continue;
					}
				}
			}

		} else if (h.precision() > node->geohash.precision()) {
			cout << "b" << endl;
			if (path.back()->is_leaf() == true) {
				for (const auto &gp : path.back()->pset) {
					cout << "b1" << endl;
					cout << gp.lat << endl;
					if (box.covers(gp.lat, gp.lon) == true) {
						a.push_back(gp);
						cout << "s1.size:";
						cout << a.size() << endl;

					}

				}
			} else {
				cout << "b2" << endl;
			}
		}

		return a;
	}

	bgeohash::coordbox coordbox() const{
		return geohash.decode();
	}


	friend ostream & operator << (ostream & out,const GeoNode & gnode){

		out << "GeoNode(";
		out << gnode.geohash.decode() << ":" << std::flush;
		//out << gnode.mid << ":" << std::flush;
		out << "{";
		int cnt = 0;

		for (const auto & gp : gnode.pset){
			out << gp << ",";
			if(++cnt > 20){
				out << "...";
				break;
			}
		}
		out << "}";
		out << endl;

		out << "s.size:";
		out << gnode.pset.size() << endl;
		out << gnode.is_leaf() << endl;


		if (gnode.left != NULL) {
			out << *(gnode.left) << std::flush; //再帰をするために必要な行
		} else {
			out << "(NULL)";
		}
		out << " 	";
		if(gnode.right != NULL){
			out << *(gnode.right) << std::flush;
		}else{
			out << "(NULL)";
		}
		return out;
	}

};


vector<geopoint> read_geopoints(const string & filename);
vector<string> split(string& input, char delimiter);

int main(int argc, char *argv[]){

	cout << "!!!Hello World!!!" << endl; // prints !!!Hello World!!!

		//double lat = 33.59494018554690, lon = 130.4036063702130;//pre=56まで
		//double lat = 33.594940, lon = 130.40360;//pre=56まで bhash=18
		//double lat = 33.6155019, lon = 130.6712318;//pre=56まで bhash=56
	    //double lat = 30.6155019, lon = 80.6155019; //bhash=2
		double lat = 33.6155, lon = 130.6712; //pre=56まで bhash=40
		//int pre = 6;

		cout << "encoding cordinate: " << lat << ", " << lon << endl;

		string hashcode = geohash::encode(lat, lon, 7);
		cout << "geohash code: " << hashcode << endl;

		bgeohash bhash(lat, lon, 41);
		cout << "bgeohash code: " << bhash << endl;
		cout << "geohash in binary: " << hex << bhash.location() << endl;
		uint64_t intval = bhash.location();
		for(unsigned int i = 0; i < bhash.precision(); ++i) {
			cout << ( (intval >> (63-i)) & 1)  << " ";
			if(((intval >> (63-i)) & 1) == 1){
				//cout << "yes" ;

			}
		}
		cout << endl;
	if (argc < 2) {
		cerr << "usage: command map-file_name]" << endl;
		exit(EXIT_FAILURE);
	}
	vector<geopoint> pset = read_geopoints(argv[1]);

	GeoNode root(bgeohash(0), pset, 40);
	cout << "p_search = " << endl;
	int cnt = 0;
	for(const auto &gp : root.search(bhash)){
		cout << gp;
		if(++cnt > 500){
		cout << "...";
		break;
		}
	}
	cout << endl;
	cout << endl;
	cout << "GeoTree = " << endl;
	cout << root << endl;
	cout << endl;
	return 0;
}

/*void preorder(vector<geopoint>T[], int id){
	if(id == NIL) return;
	cout << " " << id;
	if(T[id].left != NIL) preorder(T,T[id].left);
	if(T[id].right != NIL) preorder(T,T[id].right);
}*/

/*vector<string> preorder(vector<string> &T,int id){
			//char abcd;
			string a="abc";
		    //int str = T.push_back(abcd);
			T.push_back(GeoNode::pset);
			T.push_back("abcd");
			for (auto x: T) {
				cout << x << endl;
			}
			//string str = to_string(abcd);
			cout << "preorder=" << endl;
			//cout << str << endl;
			//preorder(out,)
			return T;
}*/


vector<string> split(string& input, char delimiter) {
    istringstream stream(input);
    string field;
    vector<string> result;
    while (getline(stream, field, delimiter)) {
        result.push_back(field);
    }
    return result;
}

vector<geopoint> read_geopoints(const string & filename){
	ifstream csvf;
	vector<geopoint> pset;
	csvf.open(filename);
	if (! csvf ) {
		cerr << "open a geograph file " << filename << " failed." << endl;
		return pset;
	}

	string line;
	while (getline(csvf, line)) {
		vector<string> strvec = split(line, ',');
		if (strvec.size() < 4) {
			cerr << "insufficient parameters to define a node_edge." << endl;
			continue;
		}
		//uint64_t id = stoull(strvec[0]);
		//pset.insert(id);
		double lat = stod(strvec[1]);
		double lon = stod(strvec[2]);
		pset.push_back(geopoint(lat,lon));
	}
	csvf.close();
	return pset;
}
