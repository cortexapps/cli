import json
from enum import Enum
from typing import List, Optional, Union

class TeamType(Enum):
    CORTEX = "CORTEX"
    IDP = "IDP"

class Team:
    class Metadata:
        def __init__(self, name: str, description: Optional[str] = None, summary: Optional[str] = None):
            self.name = name
            self.description = description
            self.summary = summary

        @classmethod
        def from_obj(cls, obj):
            return cls(
                name=obj['name'],
                description=obj.get('description'),
                summary=obj.get('summary')
            )

        def to_obj(self):
            return {
                'name': self.name,
                'description': self.description,
                'summary': self.summary
            }

    class Link:
        def __init__(self, description: str, name: str, type: str, url: str):
            self.description = description
            self.name = name
            self.type = type
            self.url = url

        @classmethod
        def from_obj(cls, obj):
            return cls(**obj)

        def to_obj(self):
            return vars(self)

    class SlackChannel:
        def __init__(self, description: str, name: str, notificationsEnabled: bool):
            self.description = description
            self.name = name
            self.notificationsEnabled = notificationsEnabled

        @classmethod
        def from_obj(cls, obj):
            return cls(**obj)

        def to_obj(self):
            return vars(self)

    class CortexMember:
        def __init__(self, email: str, name: str, description: Optional[str] = None, role: Optional[str] = None, notificationsEnabled: bool = True):
            self.email = email
            self.name = name
            self.description = description
            self.role = role
            self.notificationsEnabled = notificationsEnabled

        @classmethod
        def from_obj(cls, obj):
            return cls(**obj)

        def to_obj(self):
            return vars(self)

    class CortexTeam:
        def __init__(self, members: List['Team.CortexMember']):
            self.members = members

        @classmethod
        def from_obj(cls, obj):
            return cls(members=[Team.CortexMember.from_obj(member) for member in obj['members']])

        def to_obj(self):
            return {'members': [member.to_obj() for member in self.members]}

    class IdpGroup:
        def __init__(self, group: str, provider: str):
            self.group = group
            self.provider = provider

        @classmethod
        def from_obj(cls, obj):
            return cls(**obj)

        def to_obj(self):
            return vars(self)


    def __init__(self,
                 teamTag: str,
                 metadata_name: str,
                 type: TeamType,
                 id: Optional[str] = None,
                 links: Optional[List[Link]] = None,
                 slackChannels: Optional[List[SlackChannel]] = None,
                 cortexTeam: Optional['Team.CortexTeam'] = None,
                 idpGroup: Optional['Team.IdpGroup'] = None,
                 catalogEntityTag: Optional[str] = None,
                 metadata_description: Optional[str] = None,
                 metadata_summary: Optional[str] = None,
                 isArchived: bool = False
                 ):

        if type == TeamType.CORTEX and cortexTeam is None:
            raise ValueError("cortexTeam.members must exist if type is 'CORTEX'")

        if type == TeamType.IDP and idpGroup is None:
            raise ValueError("idpGroup must exist if type is 'IDP'")

        self.id = id
        self.teamTag = teamTag
        self.catalogEntityTag = catalogEntityTag or teamTag
        self.metadata = self.Metadata(metadata_name, metadata_description, metadata_summary)
        self.links = links or []
        self.slackChannels = slackChannels or []
        self.isArchived = isArchived
        self.cortexTeam = cortexTeam
        self.idpGroup = idpGroup
        self.type = type

    @classmethod
    def from_json(cls, data: Union[str, dict]):
        if isinstance(data, str):
            data = json.loads(data)
        return cls.from_obj(data)

    def to_json(self):
        return json.dumps(self.to_obj(), indent=4)

    @classmethod
    def from_obj(cls, obj: dict):
        type_enum = TeamType(obj['type'])

        cortex_team = None
        idp_group = None

        if type_enum == TeamType.CORTEX:
            cortex_team = cls.CortexTeam.from_obj(obj['cortexTeam'])
        elif type_enum == TeamType.IDP:
            idp_group = cls.IdpGroup.from_obj(obj['idpGroup'])

        links = [cls.Link.from_obj(link) for link in obj.get('links', [])]
        slack_channels = [cls.SlackChannel.from_obj(channel) for channel in obj.get('slackChannels', [])]

        return cls(
            teamTag=obj['teamTag'],
            metadata_name=obj['metadata']['name'],
            type=type_enum,
            links=links,
            slackChannels=slack_channels,
            cortexTeam=cortex_team,
            idpGroup=idp_group,
            id=obj.get('id'),
            catalogEntityTag=obj.get('catalogEntityTag'),
            metadata_description=obj['metadata'].get('description'),
            metadata_summary=obj['metadata'].get('summary'),
            isArchived=obj.get('isArchived', False),
        )

    def to_obj(self):
        data = {
            "id": self.id,
            "teamTag": self.teamTag,
            "catalogEntityTag": self.catalogEntityTag,
            "metadata": self.metadata.to_obj(),
            "links": [link.to_obj() for link in self.links],
            "slackChannels": [channel.to_obj() for channel in self.slackChannels],
            "isArchived": self.isArchived,
            "type": self.type.value
        }

        if self.type == TeamType.CORTEX and self.cortexTeam:
            data["cortexTeam"] = self.cortexTeam.to_obj()

        if self.type == TeamType.IDP and self.idpGroup:
            data["idpGroup"] = self.idpGroup.to_obj()

        return data

def main():
    # Creating manually
    team_manual = Team(
        teamTag="retail2-partner-experience",
        metadata_name="Retail2 Partner Experience",
        type=TeamType.CORTEX,
        links=[],
        slackChannels=[],
        cortexTeam=Team.CortexTeam(members=[])
    )
    print(json.dumps(team_manual.to_obj(), indent=4))

if (__name__ == "__main__"):
    main()
