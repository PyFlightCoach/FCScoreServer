const scoreCapabilities = {
  request: {
      operation: "scoreCapabilities"
  }
};

const scoreCapabilitiesResponse = {
  supportedRequests: {
      scoreCapabilities: {
          operation: "scoreCapabilities"
      },
      scoreManeuver: {
          operation: "scoreManeuver",
          difficulties: [1, 2, 3], // lists available
          truncate: true,  // boolean, true if supported
          total: true,
          styles: ["F3A FAI"],
          schedules: ["P25", "F25"]
      },
      analyseAndScoreManeuver: {
          operation: "analyseAndScoreManeuver",
          difficulties: [ 1, 2, 3], // lists available
          truncate: true,  // boolean, true if supported
          total: true,
          styles: [
              { style: "F3A FAI", schedules: ["P25", "F25"] }
          ]
      }

  }
};

