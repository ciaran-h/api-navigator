# API Navigator
The basic idea behind this project is to allow non-programmers to navigate and query an API using a command line interface. The output of a query can also be saved to an excel file to be further processed using the more intuitive excel commands.

## Example:

```
-- Queries an API endpoint using summoner name
nav summoners -summonerName "username"
-- Queries the matchlists endpoint using the encryptedAccountId, which was returning by the
-- previous query
nav matchlists
-- Filters the result to a single match, allowing for an identifying information stored in that
-- object to be used as a parameter in a query
filter matches[0]
-- Navigates to the matches endpoint using the matchId which was aquired by filtering the matches
nav matches
-- Find and saves the participantId for the current summoner
store participantIdentities[player.summonerName=\'{summonerName}\'].participantId participantId
-- Prints the last champion that participant above played
printq participants[{participantId}].championId
```

## TODO
- The query parsing needs to be completely remade.
