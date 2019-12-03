#include <iostream>
#include <cstdlib>
#include "DirectoryLister.h"

int main(const int argc, const char *argv[]) {
	if (argc <= 1) {
		std::cerr << "error: give a base directory name." << std::endl;
		exit(1);
	}
	const char *basepath = argv[1];
	const char namepattern[] = ".*\\.csv";

	DirectoryLister dlister(basepath);

	int counter = 0;
	if ( ! dlister() ) {
		std::cerr << "error: opendir returned a NULL pointer for the base path." << std::endl;
		exit(1);
	}

	std::vector<std::string> csvfiles;
	while (dlister.get_next_file(namepattern) != NULL) {
		csvfiles.push_back(dlister.entry_path());
	}
	for(int i = 0; i < csvfiles.size(); ++i) {
		std::cout << (i+1) << ": " << csvfiles.back().c_str() << std::endl;
	}
	std::cout << std::endl << "finished." << std::endl << std::endl;
	return 0;
}
