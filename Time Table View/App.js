"use client"
import './styles/tailwind.css';
import { 
  Day, 
  Inject, 
  Month, 
  ScheduleComponent, 
  ViewDirective, 
  ViewsDirective, 
  Week 
} from "@syncfusion/ej2-react-schedule";
import { registerLicense } from "@syncfusion/ej2-base";

registerLicense(
  "Ngo9BigBOggjHTQxAR8/V1NDaF5cWWtCf1FpRGBGfV5ycEVAal5UTnNWUj0eQnxTdEFiWH5dcnZURmJfWUd+XQ=="
);

//can add data from json
const data = [
  {
    Id: 1,
    Subject: "Sales Presentation",
    StartTime: new Date(2024, 10, 11, 10, 0),
    EndTime: new Date(2024, 10, 11, 12, 30),
    IsAllDay: false,
  },
  {
    Id: 2,
    Subject: "New Budget Report",
    StartTime: new Date(2024, 10, 10, 10, 0),
    EndTime: new Date(2024, 10, 10, 12, 30),
    IsAllDay: true,
    Status: "Completed",
    Priority: "High",
  },
];

export default function Page() {
  return (
    <main className="flex justify-center">
      <ScheduleComponent 
        width="100%"
        height={600}
        eventSettings={{ dataSource: data }}
        //selectedDate={new Date(2025, 1, 11)}  //default date is curr month, changes default to selected day
        //currentView="Month"   //default view is week, this changes default view to month
      >
        <ViewsDirective>
          <ViewDirective option="Day" />
          <ViewDirective option="Week" />
          <ViewDirective option="Month" />
        </ViewsDirective>

        <Inject services={[Day, Week, Month]} />
      </ScheduleComponent>
    </main>
  );
}
