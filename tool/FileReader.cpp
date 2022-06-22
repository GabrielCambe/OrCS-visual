#include <iostream>
#include <string>

class FileReader {
    private:
        std::string filename;
    public:
        std::string current_line;
        void open(std::string filename);
        void readline();
        void close();
};

void FileReader::open(std::string filename){

}

void FileReader::readline(){

}

void FileReader::close(){

}

int main(int argc, char **argv) {
    FileReader file;
    file.open("commands.txt");
    std::cout << file.current_line << std::endl;
    file.readline();
    std::cout << file.current_line << std::endl;
}