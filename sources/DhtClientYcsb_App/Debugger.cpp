#include <string>

#include "DhtClientApp.h"
#include "EnclaveInitializer.h"

using namespace Decent::DhtClient;

int main(int argc, char ** argv)
{
	GetDhtClientApp().Insert("TestKey", "TestVal");
	return 0;
}
