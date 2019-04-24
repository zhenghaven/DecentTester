#include "Messages.h"

#include <json/json.h>

using namespace Decent::Dht;

constexpr char const FromApp::sk_ValueCat[];

Json::Value& FromApp::GetJsonMsg(Json::Value& outJson) const
{
	Json::Value& root = SmartMessages::GetJsonMsg(outJson);

	root = Json::nullValue;

	return root;
}
