/*
 * gpspoint.cpp
 *
 *  Created on: Nov 18, 2019
 *      Author: sin
 */

#include "gpspoint.h"

double gpspoint::distanceTo(const gpspoint &q) const {
	//http://dtan4.hatenablog.com/entry/2013/06/10/013724
	//https://en.wikipedia.org/wiki/Geographical_distance#Ellipsoidal_Earth_projected_to_a_plane
	//https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
	//const int mode = 1;

	// convert degree values to radians
	double plat = DEG2RAD(lat), plon = DEG2RAD(lon),
			qlat = DEG2RAD(q.lat), qlon = DEG2RAD(q.lon);
	// 緯度と経度の差
	//double latdiff = plat - qlat, londiff = plon - qlon;
	// the average of lattitude values
	double latavr = (plat + qlat) / 2.0;

	// 測地系による値の違い
	double a = 6378137.0; //mode ? 6378137.0 : 6377397.155; // 赤道半径
	//double b = 6356752.314140356; //mode ? 6356752.314140356 : 6356078.963; // 極半径
	//$e2 = ($a*$a - $b*$b) / ($a*$a);
	double e2 = 0.00669438002301188; //mode ? 0.00669438002301188 : 0.00667436061028297; // 第一離心率^2
	//$a1e2 = $a * (1 - $e2);
	double a1e2 = 6335439.32708317; // mode ? 6335439.32708317 : 6334832.10663254; // 赤道上の子午線曲率半径

	double sin_latavr = sin(latavr);
	double W2 = 1.0 - e2 * (sin_latavr * sin_latavr);
	double M = a1e2 / (sqrt(W2) * W2); // 子午線曲率半径M
	double N = a / sqrt(W2); // 卯酉線曲率半径

	double t1 = M * (plat - qlat); //latdiff;
	double t2 = N * cos(latavr) * (plon - qlon); //londiff;
	return sqrt((t1 * t1) + (t2 * t2));
}

double gpspoint::distanceTo(const gpspoint &q1, const gpspoint &q2) const {
	if ( inner_prod(q1, q2, *this) < epsilon ) { // < 0.0
		return q1.distanceTo(*this);
	}
	if ( inner_prod(q2, q1, *this) < epsilon ) { // < 0.0
		return q2.distanceTo(*this);
	}
	return ABS(norm_outer_prod(q1, q2, *this)) / q1.distanceTo(q2);
}


std::vector<std::pair<float,float>> gpspoint::lcs(
		std::vector<gpspoint> &pseq, std::vector<gpspoint> &qseq,
		const double &bound) {
	dptable table(qseq.size(), pseq.size());
	unsigned int ip, iq; // column, row
	/*
	 *    |        |        ip          |
	 * -----------------------------------------
	 *    |        |              lp    |
	 *    |        |  ql          qp    |
	 * -----------------------------------------
	 *    |        |          :iq-1,iq  |
	 *    |        |          :   <-> ip|
	 * iq |        |....................|
	 *    |        | iq <->   :iq <->   |
	 *    |        | ip-1, ip :      ip |
	 * -----------------------------------------
	 *    |        |                    |
	 */
	// computing the top-frame and the left side-frame cells
	for (ip = 0; ip < pseq.size(); ++ip) {
		// iq == 0
		//std::cout << "(" << ip << ") " << std::flush;
		table(0, ip).clear();
		if ( qseq[0].distanceTo(pseq[ip]) <= bound )
			table(0, ip).qp = 2;
		if ( ip != 0 && qseq[0].distanceTo(pseq[ip-1], pseq[ip]) <= bound )
			table(0, ip).ql = 1;
	}
	for (iq = 0; iq < qseq.size(); ++iq) {
		// ip == 0
		table(iq, 0).clear();
		if ( pseq[0].distanceTo(qseq[iq]) <= bound)
			table(iq,0).qp = 2;
		if ( iq != 0 && pseq[0].distanceTo(qseq[iq-1], qseq[iq]) <= bound )
			table(iq,0).lp = 1;
	}

	// computing inner cells by the inductive relation
	// iq -- row, ip -- column
	for (iq = 1; iq < qseq.size(); ++iq) {
		for (ip = 1; ip < pseq.size(); ++ip) {
			table(iq,ip).clear();
			// (1) lp (iq-1, [iq <-> ip])
			if ( pseq[ip].distanceTo(qseq[iq-1],qseq[iq]) <= bound ) {
				table(iq,ip).lp = 1;
			}
			table(iq,ip).lp = MAX_AMONG3(
					table(iq-1,ip).qp,
					table(iq-1,ip).ql + table(iq,ip).lp,
					table(iq,ip-1).lp );
			// (2) ql (iq <-> [ip-1, ip])
			if ( qseq[iq].distanceTo(pseq[ip-1],pseq[ip]) <= bound )
				table(iq,ip).ql = 1;
			table(iq,ip).ql = MAX_AMONG3(
					table(iq,ip-1).qp,
					table(iq,ip-1).lp + table(iq,ip).ql,
					table(iq-1,ip).ql );
			// (3) pp
			if ( qseq[iq].distanceTo(pseq[ip]) <= bound )
				table(iq,ip).qp = 2;
			table(iq,ip).qp = MAX_AMONG3(
					table(iq,ip).lp,
					table(iq-1,ip-1).qp + table(iq,ip).qp,
					table(iq,ip).ql );
		}
	}
#ifdef SHOW_TABLE
	const unsigned int ip_start = 0;//72;
	const unsigned int ip_stop = MIN(400, (pseq.size()<<1)-1);
	printf("     ");
	for(ip = ip_start; ip < ip_stop ; ++ip) {
		printf("%3d, ", ip);
	}
	printf("\n");
	printf("     ");
	for(ip = ip_start; ip < ip_stop ; ++ip) {
		printf("-----");
	}
	printf("\n");
	for(iq = 0; iq < (qseq.size()<<1)-1; ++iq) {
		printf("%3d| ", iq);
		for(ip = ip_start; ip < ip_stop ; ++ip) {
			printf("%3d, ", dtable(iq,ip));
		}
		printf("\n");
	}
#endif
	// back track the subsequence
	std::vector<std::pair<float,float>> matchedpairs;
	ip = pseq.size() - 1;
	iq = qseq.size() - 1;
	enum subcell {
		lp = 1,
		ql = 2,
		qp = 3,
	} qpmode = qp;
	while (ip > 0 && iq > 0) {
		//skip through
		if ( qpmode == qp ) {
			if (table(iq,ip).qp == table(iq - 1,ip - 1).qp ) {
				qpmode = qp;
				ip -= 1;
				iq -= 1;
				//std::cout << "\\";
				continue;
			} else if ( table(iq,ip).qp == table(iq, ip).lp ) {
				qpmode = lp;
				//std::cout << "|";
			} else if ( table(iq, ip).qp == table(iq,ip).ql ) {
				qpmode = ql;
				//std::cout << "-";
			} else if ( table(iq, ip).qp == table(iq-1, ip-1).qp + 2) {
				matchedpairs.push_back(std::pair<float,float>(iq, ip));
				qpmode = qp;
				ip -= 1;
				iq -= 1;
				//std::cout << "*";
				continue;
			} else {
				std::cerr << "back trace error qp @ " << iq << ", " << ip << std::endl;
				break;
			}
		}
		if (qpmode == lp) {
			if ( table(iq,ip).lp == table(iq-1,ip).ql ) {
				iq -= 1;
				qpmode = ql;
				//std::cout << "\\";
			} else if ( table(iq, ip).lp == table(iq-1,ip).qp ) {
				iq -= 1;
				qpmode = qp;
				//std::cout << "|";
			} else if ( table(iq,ip).lp == table(iq,ip-1).lp ) {
				ip -= 1;
				qpmode = lp;
				//std::cout << "-";
			} else if ( table(iq,ip).lp == table(iq-1,ip).ql + 1 ) {
				matchedpairs.push_back(std::pair<float,float>((float)iq - 0.5, ip));
				iq -= 1;
				qpmode = ql;
				//std::cout << "*";
			} else {
				std::cerr << "back trace error lp @ " << iq << ", " << ip << std::endl;
				break;
			}
			continue;
		} else if (qpmode == ql) {
			if ( table(iq,ip).ql == table(iq,ip-1).lp ) {
				ip -= 1;
				qpmode = lp;
				//std::cout << "\\";
			} else if ( table(iq,ip).ql == table(iq,ip-1).qp ) {
				ip -= 1;
				qpmode = qp;
				//std::cout << "-";
			} else if ( table(iq,ip).ql == table(iq-1,ip).ql ) {
				iq -= 1;
				qpmode = ql;
				//std::cout << "|";
			} else if ( table(iq,ip).ql == table(iq,ip-1).lp + 1 ) {
				matchedpairs.push_back(std::pair<float,float>(iq, (float)ip - 0.5));
				ip -= 1;
				qpmode = lp;
				//std::cout << "*";
			} else {
				std::cerr << "back trace error ql @ " << iq << ", " << ip << std::endl;
				break;
			}
			continue;
		}
	}
	std::reverse(matchedpairs.begin(), matchedpairs.end());
	return matchedpairs;
}

/*
std::pair<int, std::vector<gpspoint::uintpair>> gpspoint::lcs1(
		std::vector<gpspoint> &pseq, std::vector<gpspoint> &qseq,
		const double &bound) {
	dptable dtable((qseq.size() << 1) - 1, (pseq.size() << 1) - 1); //[(pseq.size() << 1) - 1][(qseq.size() << 1) - 1];
	unsigned int ip, iq;
	// computing the left- and top- frame cells as base-steps
	for (ip = 0; ip < (pseq.size()<<1)-1; ++ip) {
		dtable(0,ip) = 0;
		//std::cout << "(" << ip << ") " << std::flush;
		if ( (ip & 1) == 0 ) {
			if ( qseq[0].distanceTo(pseq[ip>>1]) <= bound )
				dtable(0, ip) = 2;
		} else {
			if ( qseq[0].distanceTo(pseq[ip>>1], pseq[(ip>>1)+1]) <= bound )
				dtable(0, ip) = 1;
		}
	}
	for (iq = 0; iq < (qseq.size()<<1)-1; ++iq) {
		dtable(iq,0) = 0;
		if ( (iq & 1) == 0 ) {
			if ( pseq[0].distanceTo(qseq[iq>>1]) <= bound)
				dtable(iq,0) = 2;
		} else {
			if ( pseq[0].distanceTo(qseq[iq>>1], qseq[(iq>>1)+1]) <= bound )
				dtable(iq,0) = 1;
		}
	}
	// computing inner cells by the inductive relation
	// iq -- row, ip -- column
	for (iq = 1; iq < (qseq.size()<<1)-1; ++iq) {
		for (ip = 1; ip < (pseq.size()<<1)-1; ++ip) {
			dtable(iq,ip) = 0;
			switch ( (iq & 1)<<1 | (ip & 1) ) {
			case 0: // if ( (iq & 1) == 0 && (ip & 1) == 0 ) {
				if ( qseq[iq>>1].distanceTo(pseq[ip>>1]) <= bound ) {
					dtable(iq,ip) = 2;
					//std::cerr << iq << ", " << ip << ": " << 2 << std::endl;
				}
				dtable(iq,ip) = MAX_AMONG3(
						dtable(iq-1,ip),
						dtable(iq-1,ip-1) + dtable(iq,ip),
						dtable(iq,ip-1) );
				break;
			case 3: // else if ( (iq & 1) == 1 && (ip & 1) == 1 ) {
				dtable(iq,ip) = MAX_AMONG3(
						dtable(iq-1,ip-1),
						dtable(iq,ip-1),
						dtable(iq-1,ip) );
				break;
			case 1: // else if ( (iq & 1) == 0 && (ip & 1) == 1 ) {
				if ( qseq[iq>>1].distanceTo(pseq[ip>>1],pseq[(ip>>1)+1]) <= bound ) {
					dtable(iq,ip) = 1;
					//std::cerr << iq << ", " << ip << ": " << 1 << std::endl;
				}
				dtable(iq,ip) = MAX_AMONG3(
						dtable(iq,ip-1),
						dtable(iq-1,ip-1) + dtable(iq,ip),
						dtable(iq-1,ip) );
				break;
			case 2: // else if ( (iq & 1) == 1 && (ip & 1) == 0 ) {
				if ( pseq[ip>>1].distanceTo(qseq[iq>>1],qseq[(iq>>1)+1]) <= bound ) {
					dtable(iq,ip) = 1;
					//std::cerr << iq << ", " << ip << ": " << 1 << std::endl;
				}
				dtable(iq,ip) = MAX_AMONG3(
						dtable(iq,ip-1),
						dtable(iq-1,ip-1) + dtable(iq,ip),
						dtable(iq-1,ip) );
				break;
			}
		}
	}
#ifdef SHOW_TABLE
	const unsigned int ip_start = 0;//72;
	const unsigned int ip_stop = MIN(400, (pseq.size()<<1)-1);
	printf("     ");
	for(ip = ip_start; ip < ip_stop ; ++ip) {
		printf("%3d, ", ip);
	}
	printf("\n");
	printf("     ");
	for(ip = ip_start; ip < ip_stop ; ++ip) {
		printf("-----");
	}
	printf("\n");
	for(iq = 0; iq < (qseq.size()<<1)-1; ++iq) {
		printf("%3d| ", iq);
		for(ip = ip_start; ip < ip_stop ; ++ip) {
			printf("%3d, ", dtable(iq,ip));
		}
		printf("\n");
	}
#endif
	// back track the subsequence
	std::vector<uintpair> matchedpairs;
	ip = (pseq.size()<<1) - 2;
	iq = (qseq.size()<<1) - 2;
	while (ip > 0 && iq > 0) {
		//skip through
		if (dtable(iq,ip) == dtable(iq - 1,ip - 1)) {
			ip -= 1;
			iq -= 1;
			printf("\\");
		} else if (dtable(iq,ip) == dtable(iq,ip - 1)) {
			ip -= 1;
			printf("<");
		} else if (dtable(iq,ip) == dtable(iq - 1,ip)) {
			iq -= 1;
			printf("^");
		}
		// point-to-point or point-to-line match
		else if ( (iq & 1) == 0 && (ip & 1) == 0 ) {
			if ( dtable(iq,ip) == dtable(iq - 1,ip - 1) + 2 ) {
				matchedpairs.push_back(uintpair(iq, ip));
				printf("(%d, %d: %.1lf)", iq>>1, ip>>1, qseq[iq>>1].distanceTo(pseq[ip>>1]));
				ip -= 1;
				iq -= 1;
			} else {
				printf("%d, %d error!\n", iq, ip);
				break;
			}
		} else {
			if ( dtable(iq,ip) == dtable(iq - 1,ip - 1) + 1 ) {
				matchedpairs.push_back(uintpair(iq, ip));
				if ( (ip & 1) == 0 )
					printf("{%d, %d: %.1lf}", iq, ip, pseq[ip>>1].distanceTo(qseq[iq>>1], qseq[(iq>>1)+1]) );
				else if ( (iq & 1) == 0 )
					printf("{%d, %d: %.1lf} ", iq, ip, qseq[iq>>1].distanceTo(pseq[ip>>1], pseq[(ip>>1)+1]) );
				ip -= 1;
				iq -= 1;
			} else {
				printf("%d, %d error!\n", iq, ip);
				break;
			}
		}
	}
	std::reverse(matchedpairs.begin(), matchedpairs.end());
	return std::pair<int, std::vector<uintpair>>(
			dtable((qseq.size()<<1) - 2, (pseq.size()<<1) - 2), matchedpairs);
}
*/
