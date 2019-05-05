#include <string>
#include <memory>

#include "DhtClientApp.h"
#include "EnclaveInitializer.h"
#include "DhtClientAppPkg.h"

using namespace Decent::DhtClient;

int main(int argc, char ** argv)
{
	std::unique_ptr<DhtClientAppPkg> dhtClientAppPkg(GetNewDhtClientAppPkg(100));
	dhtClientAppPkg->m_app->Insert("TestKey1", "TestVal1");
	dhtClientAppPkg->m_app->Insert("TestKey2", "TestVal2");
	dhtClientAppPkg->m_app->Insert("TestKey3", "TestVal3");
	dhtClientAppPkg->m_app->Insert("TestKey4", "TestVal4");
	dhtClientAppPkg->m_app->Insert("TestKey5", "TestVal5");
	return 0;
}
