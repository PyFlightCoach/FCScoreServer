const scoreManeuver = {
    fcscore: {
        id: "id",    // any data that could be used later like database id, previous calculations id, user id, etc.
        userID: "userid"
    },
    request: {
        operation: "scoreManeuver",
        difficulty: 0,  // 0 - all, 1 - 1, 2 - 2, 3 -3
        optimise: true, // optimise (best) score including alignment
        truncate: true  // boolean, true - return both detailed and trancated results
    },
    flight: {
        file: "name",
        date: "date",    // from the file or upload timestamp
        pilotN: "Name",      // optional, future use
        pilotC: "Cname",      // optional, future use Country
        pilotID: "ID",      // optional, future use ID
        location: "name",      // optional, future use
        competitionID: "id",      // optional, future use
        competitionName: "name",      // optional, future use
        pilotP: { lat: 0.0, lng: 0.0, alt: 0.0 },
        centerP: { lat: 0.0, lng: 0.0, alt: 0.0 },
        originP: { lat: 0.0, lng: 0.0, alt: 0.0 },
        style: "F3A FAI",
        schedule: "P25"
    },
    site: {
        site: "name",
        rotation: "rotation",
        pilotdB: { lat: 0.0, lng: 0.0, alt: 0.0 },
        centerdB: { lat: 0.0, lng: 0.0, alt: 0.0 }
    },
    maneuver: {
        id: "id",
        shortName: "sname",
        k: "k",
        data:   [
            {
              "VN": 16.47344398498535,
              "VE": -5.338947772979736,
              "VD": -6.548651218414307,
              "dPD": -4.655212879180908,
              "r": -5.01,
              "p": 21.4,
              "yw": 323.59,
              "N": 27.562450408935547,
              "E": -14.525741577148438,
              "D": -10.117027282714844,
              "time": 496110387,
              "roll": -0.0874409955249159,
              "pitch": 0.3735004599267865,
              "yaw": 5.64771092652845
            }
        ]        
    }
};

const scoreManeuverResponse = {
    fcscore: {
        id: "id",    // any data that could be used later like database id, calculations id, user id, etc.
        userID: "userid"
    },
    requested: {
        operation: "scoreManeuver",
        difficulty: 0,  // 0 - all, 1 - 1, 2 - 2, 3 -3
        optimise: true, // optimise (best) score including alignment
        truncate: true,  // boolean, true - return both detailed and trancated results
        total: true     // boolean, true - return total score
    },
    flight: {
        file: "name",
        date: "date",    // from the file or upload timestamp
        pilotN: "Name",      // optional, future use
        pilotC: "Cname",      // optional, future use Country
        pilotID: "ID",      // optional, future use ID
        location: "name",      // optional, future use
        competitionID: "id",      // optional, future use
        competitionName: "name",      // optional, future use
        pilotP: { lat: 0.0, lng: 0.0, alt: 0.0 },
        centerP: { lat: 0.0, lng: 0.0, alt: 0.0 },
        originP: { lat: 0.0, lng: 0.0, alt: 0.0 },
        style: "F3A FAI",
        schedule: "P25"
    },
    site: {
        site: "name",
        rotation: "rotation",
        pilotdB: { lat: 0.0, lng: 0.0, alt: 0.0 },
        centerdB: { lat: 0.0, lng: 0.0, alt: 0.0 }
    },
    maneuver: {
        id: "id",
        shortName: "sname",
        k: "k",
        scores: [
            {
                difficulty:  '1',
                penalties: [0, 0, 0, 0],
                truncatedPenalties: [0, 0, 0, 0],
                score: [0, 0, 0, 0],
                truncatedScore: [0, 0, 0, 0],
                total: [0, 0, 0, 0],
                truncatedTotal: [0, 0, 0, 0]
            },
            {
                difficulty:  '2',
                penalties: [0, 0, 0, 0],
                truncatedPenalties: [0, 0, 0, 0],
                score: [0, 0, 0, 0],
                truncatedScore: [0, 0, 0, 0],
                total: [0, 0, 0, 0],
                truncatedTotal: [0, 0, 0, 0]
            },
            {
                difficulty:  '3',
                penalties: [0, 0, 0, 0],
                truncatedPenalties: [0, 0, 0, 0],
                score: [0, 0, 0, 0],
                truncatedScore: [0, 0, 0, 0],
                total: [0, 0, 0, 0],
                truncatedTotal: [0, 0, 0, 0]
            }
        ]
    }
};
