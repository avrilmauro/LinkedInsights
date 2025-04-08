const svg = d3.select("svg"),
      margin = { top: 40, right: 20, bottom: 80, left: 80 },
      width = +svg.attr("width") - margin.left - margin.right,
      height = +svg.attr("height") - margin.top - margin.bottom;

const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

d3.csv("linkedin_df.csv").then(data => {
  // Filter and clean salary + experience level
  data = data
    .filter(d => d.formatted_experience_level && !isNaN(d.normalized_salary))
    .map(d => ({
      level: d.formatted_experience_level.trim(),
      salary: +d.normalized_salary
    }));

  // Group by experience level
  const grouped = d3.group(data, d => d.level);
  const boxData = Array.from(grouped, ([level, values]) => {
    const salaries = values.map(d => d.salary).sort(d3.ascending);
    const q1 = d3.quantile(salaries, 0.25);
    const median = d3.quantile(salaries, 0.5);
    const q3 = d3.quantile(salaries, 0.75);
    const iqr = q3 - q1;
    const min = d3.min(salaries.filter(s => s >= q1 - 1.5 * iqr));
    const max = d3.max(salaries.filter(s => s <= q3 + 1.5 * iqr));

    return { level, q1, median, q3, min, max };
  });

  // X and Y scales
  const x = d3.scaleBand()
    .domain(boxData.map(d => d.level))
    .range([0, width])
    .paddingInner(0.2)
    .paddingOuter(0.1);

  const y = d3.scaleLinear()
    .domain([0, d3.max(boxData, d => d.max) * 1.1])
    .range([height, 0]);

  // X Axis
  g.append("g")
    .attr("transform", `translate(0, ${height})`)
    .attr("class", "axis")
    .call(d3.axisBottom(x))
    .selectAll("text")
    .attr("transform", "rotate(-40)")
    .style("text-anchor", "end");

  // Y Axis
  g.append("g").attr("class", "axis").call(d3.axisLeft(y));

  // Title
  svg.append("text")
    .attr("x", width / 2 + margin.left)
    .attr("y", 30)
    .attr("text-anchor", "middle")
    .style("font-size", "18px")
    .style("font-weight", "600")
    .text("Experience Level vs. Normalized Salary");

  const boxWidth = x.bandwidth();

  // Draw boxes (Q1 to Q3)
  g.selectAll(".box")
    .data(boxData)
    .enter()
    .append("rect")
    .attr("class", "box")
    .attr("x", d => x(d.level))
    .attr("y", d => y(d.q3))
    .attr("height", d => y(d.q1) - y(d.q3))
    .attr("width", boxWidth)
    .style("opacity", 0)
    .transition()
    .duration(1000)
    .style("opacity", 1);

  // Median line
  g.selectAll(".median")
    .data(boxData)
    .enter()
    .append("line")
    .attr("class", "median")
    .attr("x1", d => x(d.level))
    .attr("x2", d => x(d.level) + boxWidth)
    .attr("y1", d => y(d.median))
    .attr("y2", d => y(d.median))
    .style("opacity", 0)
    .transition()
    .duration(1000)
    .style("opacity", 1);

  // Whiskers
  g.selectAll(".whisker-top")
    .data(boxData)
    .enter()
    .append("line")
    .attr("class", "whisker")
    .attr("x1", d => x(d.level) + boxWidth / 2)
    .attr("x2", d => x(d.level) + boxWidth / 2)
    .attr("y1", d => y(d.q3))
    .attr("y2", d => y(d.max))
    .style("opacity", 0)
    .transition()
    .duration(1000)
    .style("opacity", 1);

  g.selectAll(".whisker-bottom")
    .data(boxData)
    .enter()
    .append("line")
    .attr("class", "whisker")
    .attr("x1", d => x(d.level) + boxWidth / 2)
    .attr("x2", d => x(d.level) + boxWidth / 2)
    .attr("y1", d => y(d.q1))
    .attr("y2", d => y(d.min))
    .style("opacity", 0)
    .transition()
    .duration(1000)
    .style("opacity", 1);

  // Add labels for median, min, and max
  g.selectAll(".label-median")
    .data(boxData)
    .enter()
    .append("text")
    .attr("x", d => x(d.level) + boxWidth / 2)
    .attr("y", d => y(d.median) - 5)
    .attr("text-anchor", "middle")
    .attr("font-size", "12px")
    .attr("fill", "darkred")
    .text(d => `$${Math.round(d.median).toLocaleString()}`);

  g.selectAll(".label-min")
    .data(boxData)
    .enter()
    .append("text")
    .attr("x", d => x(d.level) + boxWidth / 2)
    .attr("y", d => y(d.min) + 12)
    .attr("text-anchor", "middle")
    .attr("font-size", "11px")
    .attr("fill", "gray")
    .text(d => `Min: $${Math.round(d.min).toLocaleString()}`);

  g.selectAll(".label-max")
    .data(boxData)
    .enter()
    .append("text")
    .attr("x", d => x(d.level) + boxWidth / 2)
    .attr("y", d => y(d.max) - 5)
    .attr("text-anchor", "middle")
    .attr("font-size", "11px")
    .attr("fill", "gray")
    .text(d => `Max: $${Math.round(d.max).toLocaleString()}`);
});
