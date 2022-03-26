/*
 * geodistance.h
 *
 *  Created on: 2022/03/26
 *      Author: Sin Shimozono
 */

#ifndef GEODISTANCE_H_
#define GEODISTANCE_H_

#include <cmath>

namespace geodistance {
	constexpr double deg2rad = 3.141592653589793238462643383279502884L / 180.0;

	double distance(double plat, double plon, double qlat, double qlon) {
		//http://dtan4.hatenablog.com/entry/2013/06/10/013724
		//https://en.wikipedia.org/wiki/Geographical_distance#Ellipsoidal_Earth_projected_to_a_plane
		//https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
		//const int mode = 1;
		// 緯度，経度をラジアンに
		plat *= deg2rad;
		plon *= deg2rad;
		qlat *= deg2rad;
		qlon *= deg2rad;
		// 緯度と経度の差
		//double latdiff = plat - qlat, londiff = plon - qlon;
		// 平均緯度
		double latavr = (plat + qlat) / 2.0;

		double a = 6378137.0; // 赤道半径
		double f = 1/298.257222101;  // 扁平率
		//double b = 6356752.314140356; // 極半径
		//$e^2 = ($a*$a - $b*$b) / ($a*$a);
		double e2 = 0.00669438002301188; // 第一離心率^2
		//$a1e2 = $a * (1 - $e2);
		double a1e2 = 6335439.32708317; // mode ? 6335439.32708317 : 6334832.10663254; // 赤道上の子午線曲率半径

		double sin_latavr = sin(latavr);
		double W2 = 1.0 - e2 * (sin_latavr*sin_latavr);
		double M = a1e2 / (sqrt(W2)*W2); // 子午線曲率半径M
		double N = a / sqrt(W2); // 卯酉線曲率半径

		double t1 = M * (plat - qlat); //latdiff;
		double t2 = N * cos(latavr) * (plon - qlon); //londiff;
		return sqrt((t1*t1) + (t2*t2));
	}
};

#endif /* GEODISTANCE_H_ */
