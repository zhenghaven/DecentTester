#pragma once

#include <DecentApi/CommonApp/Net/SmartMessages.h>

namespace Decent
{
	namespace DhtClient
	{
		class FromApp : public Decent::Net::SmartMessages
		{
		public:
			static constexpr char const sk_ValueCat[] = "Dht::FromApp";

		public:
			FromApp() :
				SmartMessages()
			{}

			FromApp(const Json::Value& msg) :
				SmartMessages(msg, sk_ValueCat)
			{}

			~FromApp()
			{}

			virtual std::string GetMessageCategoryStr() const override { return sk_ValueCat; }

		protected:
			virtual Json::Value& GetJsonMsg(Json::Value& outJson) const override;

		};
	}
}
