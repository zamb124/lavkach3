document.addEventListener("DOMContentLoaded", function () {
  // -----------------------------------------------------------------------
  // Users Area
  // -----------------------------------------------------------------------
  var options = {
    chart: {
      id: "customers",
      type: "area",
      height: 91,
      sparkline: {
        enabled: true,
      },
      group: "sparklines",
      fontFamily: "inherit",
      foreColor: "#adb0bb",
    },
    series: [
      {
        name: "Users",
        color: "var(--bs-secondary)",
        data: [36, 45, 31, 47, 38, 43],
      },
    ],
    stroke: {
      curve: "smooth",
      width: 2,
    },
    fill: {
      type: "gradient",
      color: "var(--bs-secondary)",

      gradient: {
        shadeIntensity: 0,
        inverseColors: false,
        opacityFrom: 0.2,
        opacityTo: 0.1,
        stops: [100],
      },
    },

    markers: {
      size: 0,
    },
    tooltip: {
      theme: "dark",
      fixed: {
        enabled: true,
        position: "right",
      },
      x: {
        show: false,
      },
    },
  };
  new ApexCharts(document.querySelector("#users"), options).render();

  // -----------------------------------------------------------------------
  // Subscriptions
  // -----------------------------------------------------------------------

  var total_orders = {
    series: [
      {
        name: "Site A",
        data: [29, 52, 38, 47, 56, 41, 46],
      },
      {
        name: "Site B",
        data: [71, 71, 71, 71, 71, 71, 71],
      },
    ],
    chart: {
      fontFamily: "inherit",
      foreColor: "#adb0bb",
      type: "bar",
      height: 98,
      stacked: true,
      offsetX: -10,
      toolbar: {
        show: false,
      },
      sparkline: {
        enabled: true,
      },
    },
    colors: ["var(--bs-white)", "rgba(255,255,255,0.5)"],
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: "26%",
        borderRadius: [3],
        borderRadiusApplication: "end",
        borderRadiusWhenStacked: "all",
      },
    },
    dataLabels: {
      enabled: false,
    },
    tooltip: {
      theme: "dark",
    },
    legend: {
      show: false,
    },
  };

  var chart_column_stacked = new ApexCharts(
    document.querySelector("#subscriptions"),
    total_orders
  );
  chart_column_stacked.render();

  // -----------------------------------------------------------------------
  // Subscriptions
  // -----------------------------------------------------------------------
  var chart = {
    series: [
      {
        name: "2024",
        data: [1.2, 2.7, 1, 3.6, 2.1, 2.7, 2.2, 1.3, 2.5],
      },
      {
        name: "2023",
        data: [-2.8, -1.1, -2.5, -1.5, -2.3, -1.9, -1, -2.1, -1.3],
      },
    ],
    chart: {
      toolbar: {
        show: false,
      },
      type: "bar",
      fontFamily: "inherit",
      foreColor: "#adb0bb",
      height: 295,
      stacked: true,
      offsetX: -15,
    },
    colors: ["var(--bs-primary)", "var(--bs-danger)"],
    plotOptions: {
      bar: {
        horizontal: false,
        barHeight: "60%",
        columnWidth: "15%",
        borderRadius: [6],
        borderRadiusApplication: "end",
        borderRadiusWhenStacked: "all",
      },
    },
    dataLabels: {
      enabled: false,
    },
    legend: {
      show: false,
    },
    grid: {
      show: true,
      padding: {
        top: 0,
        bottom: 0,
        right: 0,
      },
      borderColor: "rgba(0,0,0,0.05)",
      xaxis: {
        lines: {
          show: true,
        },
      },
      yaxis: {
        lines: {
          show: true,
        },
      },
    },
    yaxis: {
      min: -5,
      max: 5,
    },
    xaxis: {
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
      categories: [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "July",
        "Aug",
        "Sep",
      ],
      labels: {
        style: { fontSize: "13px", colors: "#adb0bb", fontWeight: "400" },
      },
    },
    yaxis: {
      tickAmount: 4,
    },
    tooltip: {
      theme: "dark",
    },
  };

  var chart = new ApexCharts(
    document.querySelector("#revenue-forecast"),
    chart
  );
  chart.render();

  // -----------------------------------------------------------------------
  // Annual Profit
  // -----------------------------------------------------------------------
  var options = {
    chart: {
      id: "annual-profit",
      type: "area",
      height: 80,
      sparkline: {
        enabled: true,
      },
      group: "sparklines",
      fontFamily: "inherit",
      foreColor: "#adb0bb",
    },
    series: [
      {
        name: "Users",
        color: "var(--bs-primary)",
        data: [25, 66, 20, 40, 12, 58, 20],
      },
    ],
    stroke: {
      curve: "smooth",
      width: 2,
    },
    fill: {
      type: "gradient",
      color: "var(--bs-primary)",

      gradient: {
        shadeIntensity: 0,
        inverseColors: false,
        opacityFrom: 0.1,
        opacityTo: 0.1,
        stops: [100],
      },
    },

    markers: {
      size: 0,
    },
    tooltip: {
      theme: "dark",
      fixed: {
        enabled: true,
        position: "right",
      },
      x: {
        show: false,
      },
    },
  };
  new ApexCharts(document.querySelector("#annual-profit"), options).render();

  // -----------------------------------------------------------------------
  // Total Income
  // -----------------------------------------------------------------------
  var customers = {
    chart: {
      id: "sparkline3",
      type: "line",
      fontFamily: "inherit",
      foreColor: "#adb0bb",
      height: 60,
      sparkline: {
        enabled: true,
      },
      group: "sparklines",
    },
    series: [
      {
        name: "Income",
        color: "var(--bs-danger)",
        data: [30, 25, 35, 20, 30, 40],
      },
    ],
    stroke: {
      curve: "smooth",
      width: 2,
    },
    markers: {
      size: 0,
    },
    tooltip: {
      theme: "dark",
      fixed: {
        enabled: true,
        position: "right",
      },
      x: {
        show: false,
      },
    },
  };
  new ApexCharts(document.querySelector("#total-income"), customers).render();

  // -----------------------------------------------------------------------
  // Weekly Scheduels
  // -----------------------------------------------------------------------
  var weekly = {
    series: [
      {
        data: [
          {
            x: "Sun",
            y: [
              new Date("2024-02-27").getTime(),
              new Date("2024-03-04").getTime(),
            ],
            fillColor: "var(--bs-primary)",
          },
          {
            x: "Mon",
            y: [
              new Date("2024-03-04").getTime(),
              new Date("2024-03-10").getTime(),
            ],
            fillColor: "var(--bs-muted)",
          },
          {
            x: "Tue",
            y: [
              new Date("2024-03-01").getTime(),
              new Date("2024-03-06").getTime(),
            ],
            fillColor: "var(--bs-danger)",
          },
        ],
      },
    ],
    chart: {
      id: "sparkline3",
      type: "rangeBar",
      fontFamily: "inherit",
      foreColor: "#adb0bb",
      height: 300,
      toolbar: {
        show: false,
      },
    },
    plotOptions: {
      bar: {
        horizontal: true,
        distributed: true,
        dataLabels: {
          hideOverflowingLabels: false,
        },
      },
    },
    dataLabels: {
      enabled: true,
      background: {
        borderRadius: 20,
      },
      formatter: function (val, opts) {
        var label = opts.w.globals.labels[opts.dataPointIndex];
        var a = moment(val[0]);
        var b = moment(val[1]);

        return label + ": " + "Meeting with Sunil";
      },
    },
    xaxis: {
      type: "datetime",
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
      labels: {
        style: { fontSize: "13px", colors: "#adb0bb", fontWeight: "400" },
      },
    },
    yaxis: {
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
      labels: {
        style: { fontSize: "13px", colors: "#adb0bb", fontWeight: "400" },
      },
    },
    grid: {
      borderColor: "rgba(0,0,0,0.05)",
    },
    tooltip: {
      theme: "dark",
    },
  };
  new ApexCharts(document.querySelector("#weekly-schedules"), weekly).render();

  // -----------------------------------------------------------------------
  // This is for the map
  // -----------------------------------------------------------------------

  $("#usa").vectorMap({
    map: "us_aea_en",
    backgroundColor: "transparent",
    zoomOnScroll: false,
    regionStyle: {
      initial: {
        fill: "#D1DBE5",
      },
    },
    markers: [
      {
        latLng: [40.71, -74.0],
        name: "Newyork",
        style: { fill: "#14e9e2" },
      },
      {
        latLng: [30.51, -91.52],
        name: "Louisiana",
        style: { fill: "#1e88e5" },
      },
      {
        latLng: [39.01, -98.48],
        name: "Kansas",
        style: { fill: "#ffd648" },
      },
      {
        latLng: [34.04, -111.09],
        name: "Arizona ",
        style: { fill: "#ff6692" },
      },
    ],
  });

  // =====================================
  // Weekly Stats
  // =====================================
  var options = {
    series: [
      {
        name: "Weekly Stats",
        data: [20, 15, 18, 25, 10, 15, 20],
      },
    ],

    chart: {
      toolbar: {
        show: false,
      },

      height: 220,
      type: "bar",
      offsetX: -30,
      fontFamily: "inherit",
      foreColor: "#adb0bb",
    },
    colors: [
      "var(--bs-gray-100)",
      "var(--bs-gray-100)",
      "var(--bs-gray-100)",
      "var(--bs-primary)",
      "var(--bs-gray-100)",
      "var(--bs-gray-100)",
      "var(--bs-gray-100)",
    ],
    plotOptions: {
      bar: {
        borderRadius: 5,
        columnWidth: "55%",
        distributed: true,
        endingShape: "rounded",
      },
    },

    dataLabels: {
      enabled: false,
    },
    legend: {
      show: false,
    },
    grid: {
      yaxis: {
        lines: {
          show: false,
        },
      },
      xaxis: {
        lines: {
          show: false,
        },
      },
    },
    xaxis: {
      categories: [
        ["Apr"],
        ["May"],
        ["June"],
        ["July"],
        ["Aug"],
        ["Sept"],
        ["Oct"],
      ],
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
    },
    yaxis: {
      labels: {
        show: false,
      },
    },
    tooltip: {
      theme: "dark",
    },
  };

  var chart = new ApexCharts(document.querySelector("#weekly-stats"), options);
  chart.render();
});
