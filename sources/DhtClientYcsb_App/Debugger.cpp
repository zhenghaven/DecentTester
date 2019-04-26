#include <string>
#include <memory>

#include "DhtClientApp.h"
#include "EnclaveInitializer.h"

using namespace Decent::DhtClient;

int main(int argc, char ** argv)
{
	std::unique_ptr<DhtClientApp> dhtClientApp(GetNewDhtClientApp());
	dhtClientApp->Insert("TestKey", "TestVal");
	return 0;
}
