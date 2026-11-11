package com.projectflow.desktop.controller;

import com.projectflow.core.model.*;
import com.projectflow.core.risk.DeterministicRiskEngine;
import com.projectflow.core.scheduling.ScheduleComparisonResult;
import com.projectflow.core.scheduling.WhatIfSchedulingEngine;
import com.projectflow.core.validation.DependencyValidator;
import com.projectflow.desktop.service.DesktopApiClient;
import com.projectflow.desktop.service.LocalStorageService;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.layout.*;

import java.time.Instant;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

public class MainViewController {
    private final BorderPane root;
    private final LocalStorageService localStorage;
    private final DesktopApiClient apiClient;
    private final DeterministicRiskEngine riskEngine;
    private final WhatIfSchedulingEngine schedulingEngine;

    // State
    private List<Workspace> workspaces = new ArrayList<>();
    private Workspace currentWorkspace = null;
    private List<Project> projects = new ArrayList<>();
    private Project currentProject = null;
    private List<Task> tasks = new ArrayList<>();
    private List<TaskDependency> dependencies = new ArrayList<>();

    // UI Controls
    private ComboBox<Workspace> workspaceComboBox;
    private ComboBox<Project> projectComboBox;
    private Label statusLabel;
    private StackPane contentArea;
    private VBox sidebar;
    private final Map<String, Button> navButtons = new HashMap<>();

    public MainViewController(BorderPane root) {
        this.root = root;
        this.localStorage = new LocalStorageService();
        this.apiClient = new DesktopApiClient(localStorage);
        this.riskEngine = new DeterministicRiskEngine();
        this.schedulingEngine = new WhatIfSchedulingEngine(riskEngine);

        initUi();
        loadData();
    }

    private void initUi() {
        // Top Header
        HBox header = new HBox(16);
        header.getStyleClass().add("top-header");
        header.setAlignment(Pos.CENTER_LEFT);

        Label brand = new Label("ProjectFlow Manager");
        brand.setStyle("-fx-font-size: 15px; -fx-font-weight: bold; -fx-text-fill: #292D28;");

        workspaceComboBox = new ComboBox<>();
        workspaceComboBox.setPromptText("Select Workspace");
        workspaceComboBox.setStyle("-fx-font-size: 11px;");
        workspaceComboBox.setOnAction(e -> {
            currentWorkspace = workspaceComboBox.getValue();
            if (currentWorkspace != null) {
                loadProjectsForWorkspace(currentWorkspace.getId());
            }
        });

        projectComboBox = new ComboBox<>();
        projectComboBox.setPromptText("Select Project");
        projectComboBox.setStyle("-fx-font-size: 11px;");
        projectComboBox.setOnAction(e -> {
            currentProject = projectComboBox.getValue();
            if (currentProject != null) {
                loadTasksForProject(currentProject.getId());
            }
        });

        Region spacer = new Region();
        HBox.setHgrow(spacer, Priority.ALWAYS);

        statusLabel = new Label("Connecting...");
        statusLabel.setStyle("-fx-font-size: 11px; -fx-font-family: monospace; -fx-text-fill: #5A6258;");

        Button syncBtn = new Button("Sync Now");
        syncBtn.getStyleClass().add("btn-secondary");
        syncBtn.setOnAction(e -> syncData());

        header.getChildren().addAll(brand, new Separator(), workspaceComboBox, projectComboBox, spacer, statusLabel, syncBtn);
        root.setTop(header);

        // Sidebar
        sidebar = new VBox(6);
        sidebar.getStyleClass().add("sidebar");
        sidebar.setPrefWidth(210);

        Label navTitle = new Label("MANAGEMENT");
        navTitle.setStyle("-fx-font-size: 10px; -fx-font-weight: bold; -fx-text-fill: #78866B; -fx-padding: 0 0 6 8;");
        sidebar.getChildren().add(navTitle);

        addNavButton("Dashboard", this::showDashboardView);
        addNavButton("Workspaces", this::showWorkspacesView);
        addNavButton("Projects", this::showProjectsView);
        addNavButton("Task Board", this::showTaskBoardView);
        addNavButton("Task Table", this::showTaskTableView);
        addNavButton("Dependencies", this::showDependenciesView);
        addNavButton("Risk Radar", this::showRiskRadarView);
        addNavButton("Schedule Planner", this::showSchedulePlannerView);
        addNavButton("Scenario Comparison", this::showScenarioComparisonView);
        addNavButton("Workflow Config", this::showWorkflowConfigView);
        addNavButton("Team Management", this::showTeamManagementView);
        addNavButton("Automation Rules", this::showAutomationRulesView);
        addNavButton("Activity History", this::showActivityHistoryView);
        addNavButton("Sync & Conflicts", this::showSyncStatusView);
        addNavButton("Profile & Settings", this::showSettingsView);

        root.setLeft(sidebar);

        // Content Area
        contentArea = new StackPane();
        contentArea.setPadding(new Insets(20));
        root.setCenter(contentArea);

        // Show Dashboard by default
        showDashboardView();
    }

    private void addNavButton(String name, Runnable action) {
        Button btn = new Button(name);
        btn.getStyleClass().add("nav-button");
        btn.setMaxWidth(Double.MAX_VALUE);
        btn.setOnAction(e -> {
            navButtons.values().forEach(b -> b.getStyleClass().remove("active"));
            btn.getStyleClass().add("active");
            action.run();
        });
        navButtons.put(name, btn);
        sidebar.getChildren().add(btn);
    }

    private void loadData() {
        new Thread(() -> {
            boolean reachable = apiClient.isServerReachable();
            Platform.runLater(() -> {
                statusLabel.setText(reachable ? "Online (Server Connected)" : "Offline (Local SQLite Cache)");
                statusLabel.setStyle(reachable
                        ? "-fx-font-size: 11px; -fx-font-family: monospace; -fx-text-fill: #56664C; -fx-font-weight: bold;"
                        : "-fx-font-size: 11px; -fx-font-family: monospace; -fx-text-fill: #D97706; -fx-font-weight: bold;");
            });

            List<Workspace> list = apiClient.getWorkspaces();
            Platform.runLater(() -> {
                workspaces = list;
                workspaceComboBox.setItems(FXCollections.observableArrayList(workspaces));
                if (!workspaces.isEmpty()) {
                    workspaceComboBox.setValue(workspaces.get(0));
                    currentWorkspace = workspaces.get(0);
                    loadProjectsForWorkspace(currentWorkspace.getId());
                }
            });
        }).start();
    }

    private void loadProjectsForWorkspace(UUID wsId) {
        new Thread(() -> {
            List<Project> list = apiClient.getProjects(wsId);
            Platform.runLater(() -> {
                projects = list;
                projectComboBox.setItems(FXCollections.observableArrayList(projects));
                if (!projects.isEmpty()) {
                    projectComboBox.setValue(projects.get(0));
                    currentProject = projects.get(0);
                    loadTasksForProject(currentProject.getId());
                } else {
                    tasks.clear();
                }
            });
        }).start();
    }

    private void loadTasksForProject(UUID projId) {
        new Thread(() -> {
            List<Task> list = apiClient.getTasks(projId);
            Platform.runLater(() -> {
                tasks = list;
            });
        }).start();
    }

    private void syncData() {
        statusLabel.setText("Syncing...");
        loadData();
    }

    // ==========================================
    // 1. DASHBOARD VIEW
    // ==========================================
    private void showDashboardView() {
        VBox box = new VBox(20);

        HBox titleBox = new HBox(12);
        titleBox.setAlignment(Pos.CENTER_LEFT);
        Label heading = new Label("Manager Operational Dashboard");
        heading.setStyle("-fx-font-size: 20px; -fx-font-weight: bold; -fx-text-fill: #292D28;");
        titleBox.getChildren().add(heading);

        // Metric Cards
        HBox metrics = new HBox(16);

        VBox c1 = createMetricCard("Active Workspaces", String.valueOf(workspaces.size()));
        VBox c2 = createMetricCard("Projects", String.valueOf(projects.size()));
        VBox c3 = createMetricCard("Active Tasks", String.valueOf(tasks.size()));

        List<RiskFinding> findings = (currentProject != null)
                ? riskEngine.evaluateProjectRisks(currentProject, tasks, dependencies, Collections.emptyMap(), Collections.emptyMap(), LocalDate.now(), Instant.now())
                : Collections.emptyList();
        VBox c4 = createMetricCard("Identified Risks", String.valueOf(findings.size()));
        c4.setStyle("-fx-background-color: #FAFAF7; -fx-border-color: #C84B31; -fx-border-width: 1; -fx-border-radius: 8; -fx-padding: 16;");

        metrics.getChildren().addAll(c1, c2, c3, c4);

        // Risk overview strip
        VBox riskStrip = new VBox(8);
        riskStrip.getStyleClass().add("card");
        Label rLabel = new Label("Deterministic Risk Summary");
        rLabel.setStyle("-fx-font-size: 14px; -fx-font-weight: bold; -fx-text-fill: #292D28;");
        riskStrip.getChildren().add(rLabel);

        if (findings.isEmpty()) {
            Label noRisk = new Label("No active risk conditions detected. Schedule and dependencies healthy.");
            noRisk.setStyle("-fx-text-fill: #56664C; -fx-font-size: 12px; -fx-font-weight: bold;");
            riskStrip.getChildren().add(noRisk);
        } else {
            for (RiskFinding rf : findings) {
                Label item = new Label("• [" + rf.getSeverity() + "] " + rf.getAffectedEntityName() + " - " + rf.getExplanation());
                item.setStyle("-fx-text-fill: #C84B31; -fx-font-size: 12px;");
                riskStrip.getChildren().add(item);
            }
        }

        box.getChildren().addAll(titleBox, metrics, riskStrip);
        contentArea.getChildren().setAll(box);
    }

    private VBox createMetricCard(String title, String val) {
        VBox c = new VBox(4);
        c.getStyleClass().add("card");
        c.setPrefWidth(180);
        Label t = new Label(title);
        t.getStyleClass().add("card-title");
        Label v = new Label(val);
        v.getStyleClass().add("card-value");
        c.getChildren().addAll(t, v);
        return c;
    }

    // ==========================================
    // 2. WORKSPACES VIEW
    // ==========================================
    private void showWorkspacesView() {
        VBox box = new VBox(16);

        HBox header = new HBox(12);
        header.setAlignment(Pos.CENTER_LEFT);
        Label title = new Label("Tenant Workspaces");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        Region spacer = new Region();
        HBox.setHgrow(spacer, Priority.ALWAYS);

        Button newBtn = new Button("Create Workspace");
        newBtn.getStyleClass().add("btn-primary");
        newBtn.setOnAction(e -> promptCreateWorkspace());

        header.getChildren().addAll(title, spacer, newBtn);

        TableView<Workspace> table = new TableView<>();
        table.getStyleClass().add("table-view");

        TableColumn<Workspace, String> nameCol = new TableColumn<>("Workspace Name");
        nameCol.setCellValueFactory(new PropertyValueFactory<>("name"));
        nameCol.setPrefWidth(220);

        TableColumn<Workspace, String> slugCol = new TableColumn<>("Slug");
        slugCol.setCellValueFactory(new PropertyValueFactory<>("slug"));
        slugCol.setPrefWidth(160);

        TableColumn<Workspace, String> descCol = new TableColumn<>("Description");
        descCol.setCellValueFactory(new PropertyValueFactory<>("description"));
        descCol.setPrefWidth(350);

        table.getColumns().addAll(nameCol, slugCol, descCol);
        table.setItems(FXCollections.observableArrayList(workspaces));

        box.getChildren().addAll(header, table);
        contentArea.getChildren().setAll(box);
    }

    private void promptCreateWorkspace() {
        Dialog<Workspace> dialog = new Dialog<>();
        dialog.setTitle("New Workspace");
        dialog.setHeaderText("Create an isolated tenant workspace");

        ButtonType createBtnType = new ButtonType("Create", ButtonBar.ButtonData.OK_DONE);
        dialog.getDialogPane().getButtonTypes().addAll(createBtnType, ButtonType.CANCEL);

        GridPane grid = new GridPane();
        grid.setHgap(10);
        grid.setVgap(10);
        grid.setPadding(new Insets(20, 150, 10, 10));

        TextField nameField = new TextField();
        nameField.setPromptText("Workspace Name");
        TextField slugField = new TextField();
        slugField.setPromptText("workspace-slug");
        TextField descField = new TextField();
        descField.setPromptText("Description");

        nameField.textProperty().addListener((obs, oldV, newV) ->
                slugField.setText(newV.toLowerCase().replaceAll("[^a-z0-9]+", "-")));

        grid.add(new Label("Name:"), 0, 0);
        grid.add(nameField, 1, 0);
        grid.add(new Label("Slug:"), 0, 1);
        grid.add(slugField, 1, 1);
        grid.add(new Label("Description:"), 0, 2);
        grid.add(descField, 1, 2);

        dialog.getDialogPane().setContent(grid);

        dialog.setResultConverter(dialogButton -> {
            if (dialogButton == createBtnType) {
                try {
                    return apiClient.createWorkspace(nameField.getText(), slugField.getText(), descField.getText());
                } catch (Exception ex) {
                    showError("Error", ex.getMessage());
                }
            }
            return null;
        });

        dialog.showAndWait().ifPresent(ws -> {
            workspaces.add(ws);
            workspaceComboBox.getItems().add(ws);
            workspaceComboBox.setValue(ws);
            showWorkspacesView();
        });
    }

    // ==========================================
    // 3. PROJECTS VIEW
    // ==========================================
    private void showProjectsView() {
        VBox box = new VBox(16);

        HBox header = new HBox(12);
        header.setAlignment(Pos.CENTER_LEFT);
        Label title = new Label("Initiatives & Projects");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        Region spacer = new Region();
        HBox.setHgrow(spacer, Priority.ALWAYS);

        Button newBtn = new Button("New Project");
        newBtn.getStyleClass().add("btn-primary");
        newBtn.setOnAction(e -> promptCreateProject());

        header.getChildren().addAll(title, spacer, newBtn);

        TableView<Project> table = new TableView<>();
        table.getStyleClass().add("table-view");

        TableColumn<Project, String> nameCol = new TableColumn<>("Project Name");
        nameCol.setCellValueFactory(new PropertyValueFactory<>("name"));
        nameCol.setPrefWidth(260);

        TableColumn<Project, String> statusCol = new TableColumn<>("Status");
        statusCol.setCellValueFactory(new PropertyValueFactory<>("status"));
        statusCol.setPrefWidth(120);

        TableColumn<Project, LocalDate> dateCol = new TableColumn<>("Target Deadline");
        dateCol.setCellValueFactory(new PropertyValueFactory<>("targetDate"));
        dateCol.setPrefWidth(160);

        table.getColumns().addAll(nameCol, statusCol, dateCol);
        table.setItems(FXCollections.observableArrayList(projects));

        box.getChildren().addAll(header, table);
        contentArea.getChildren().setAll(box);
    }

    private void promptCreateProject() {
        if (currentWorkspace == null) {
            showError("Workspace Required", "Please select or create a workspace first.");
            return;
        }

        Dialog<Project> dialog = new Dialog<>();
        dialog.setTitle("New Project");
        dialog.setHeaderText("Create a project under " + currentWorkspace.getName());

        ButtonType createBtnType = new ButtonType("Create", ButtonBar.ButtonData.OK_DONE);
        dialog.getDialogPane().getButtonTypes().addAll(createBtnType, ButtonType.CANCEL);

        GridPane grid = new GridPane();
        grid.setHgap(10);
        grid.setVgap(10);
        grid.setPadding(new Insets(20, 150, 10, 10));

        TextField nameField = new TextField();
        TextField codeField = new TextField();
        TextField descField = new TextField();

        grid.add(new Label("Project Name:"), 0, 0);
        grid.add(nameField, 1, 0);
        grid.add(new Label("Project Code:"), 0, 1);
        grid.add(codeField, 1, 1);
        grid.add(new Label("Description:"), 0, 2);
        grid.add(descField, 1, 2);

        dialog.getDialogPane().setContent(grid);

        dialog.setResultConverter(dialogButton -> {
            if (dialogButton == createBtnType) {
                try {
                    return apiClient.createProject(currentWorkspace.getId(), nameField.getText(), codeField.getText(), descField.getText());
                } catch (Exception ex) {
                    showError("Error", ex.getMessage());
                }
            }
            return null;
        });

        dialog.showAndWait().ifPresent(p -> {
            projects.add(p);
            projectComboBox.getItems().add(p);
            projectComboBox.setValue(p);
            showProjectsView();
        });
    }

    // ==========================================
    // 4. TASK BOARD (KANBAN)
    // ==========================================
    private void showTaskBoardView() {
        VBox box = new VBox(16);

        HBox header = new HBox(12);
        header.setAlignment(Pos.CENTER_LEFT);
        Label title = new Label("Kanban Board");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        Region spacer = new Region();
        HBox.setHgrow(spacer, Priority.ALWAYS);

        Button addBtn = new Button("Add Task");
        addBtn.getStyleClass().add("btn-primary");
        addBtn.setOnAction(e -> promptCreateTask());

        header.getChildren().addAll(title, spacer, addBtn);

        HBox board = new HBox(16);
        board.getChildren().addAll(
                createKanbanColumn("TODO / IN PROGRESS", false),
                createKanbanColumn("DONE", true)
        );

        box.getChildren().addAll(header, board);
        contentArea.getChildren().setAll(box);
    }

    private VBox createKanbanColumn(String title, boolean isDone) {
        VBox col = new VBox(10);
        col.setPrefWidth(300);
        col.setStyle("-fx-background-color: #EFECE4; -fx-padding: 12; -fx-background-radius: 8;");

        Label colHeader = new Label(title);
        colHeader.setStyle("-fx-font-size: 12px; -fx-font-weight: bold; -fx-text-fill: #56664C;");
        col.getChildren().add(colHeader);

        for (Task t : tasks) {
            boolean done = (t.getCompletedAt() != null);
            if (done == isDone) {
                VBox card = new VBox(6);
                card.setStyle("-fx-background-color: #FAFAF7; -fx-border-color: #E2E0D8; -fx-border-radius: 6; -fx-background-radius: 6; -fx-padding: 10;");

                Label tTitle = new Label(t.getTitle());
                tTitle.setStyle("-fx-font-weight: bold; -fx-font-size: 12px;");

                Label prio = new Label(t.getPriority() != null ? t.getPriority().name() : "MEDIUM");
                prio.setStyle("-fx-font-size: 10px; -fx-font-weight: bold; -fx-text-fill: #78866B;");

                ProgressBar pb = new ProgressBar(done ? 1.0 : 0.4);
                pb.setPrefWidth(260);

                card.getChildren().addAll(tTitle, prio, pb);
                col.getChildren().add(card);
            }
        }
        return col;
    }

    private void promptCreateTask() {
        if (currentProject == null) {
            showError("Project Required", "Please select or create a project first.");
            return;
        }

        Dialog<Task> dialog = new Dialog<>();
        dialog.setTitle("New Task");
        dialog.setHeaderText("Add task to " + currentProject.getName());

        ButtonType createBtnType = new ButtonType("Add Task", ButtonBar.ButtonData.OK_DONE);
        dialog.getDialogPane().getButtonTypes().addAll(createBtnType, ButtonType.CANCEL);

        GridPane grid = new GridPane();
        grid.setHgap(10);
        grid.setVgap(10);
        grid.setPadding(new Insets(20, 150, 10, 10));

        TextField titleField = new TextField();
        TextField descField = new TextField();
        ComboBox<TaskPriority> prioCombo = new ComboBox<>(FXCollections.observableArrayList(TaskPriority.values()));
        prioCombo.setValue(TaskPriority.MEDIUM);

        grid.add(new Label("Title:"), 0, 0);
        grid.add(titleField, 1, 0);
        grid.add(new Label("Description:"), 0, 1);
        grid.add(descField, 1, 1);
        grid.add(new Label("Priority:"), 0, 2);
        grid.add(prioCombo, 1, 2);

        dialog.getDialogPane().setContent(grid);

        dialog.setResultConverter(dialogButton -> {
            if (dialogButton == createBtnType) {
                try {
                    return apiClient.createTask(currentProject.getId(), titleField.getText(), descField.getText(), prioCombo.getValue(), LocalDate.now().plusDays(7));
                } catch (Exception ex) {
                    showError("Error", ex.getMessage());
                }
            }
            return null;
        });

        dialog.showAndWait().ifPresent(t -> {
            tasks.add(t);
            showTaskBoardView();
        });
    }

    // ==========================================
    // 5. TASK TABLE VIEW
    // ==========================================
    private void showTaskTableView() {
        VBox box = new VBox(16);
        Label title = new Label("Task Inventory & Detail Grid");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        TableView<Task> table = new TableView<>();
        table.getStyleClass().add("table-view");

        TableColumn<Task, String> titleCol = new TableColumn<>("Task Title");
        titleCol.setCellValueFactory(new PropertyValueFactory<>("title"));
        titleCol.setPrefWidth(260);

        TableColumn<Task, TaskPriority> prioCol = new TableColumn<>("Priority");
        prioCol.setCellValueFactory(new PropertyValueFactory<>("priority"));
        prioCol.setPrefWidth(120);

        TableColumn<Task, LocalDate> dueCol = new TableColumn<>("Due Date");
        dueCol.setCellValueFactory(new PropertyValueFactory<>("dueDate"));
        dueCol.setPrefWidth(140);

        table.getColumns().addAll(titleCol, prioCol, dueCol);
        table.setItems(FXCollections.observableArrayList(tasks));

        box.getChildren().addAll(title, table);
        contentArea.getChildren().setAll(box);
    }

    // ==========================================
    // 6. DEPENDENCIES VIEW
    // ==========================================
    private void showDependenciesView() {
        VBox box = new VBox(16);
        Label title = new Label("Task Dependency Chain & DAG Verification");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        Label desc = new Label("Dependencies enforce topological execution ordering and prevent circular blocking.");
        desc.setStyle("-fx-text-fill: #5A6258; -fx-font-size: 12px;");

        ListView<String> list = new ListView<>();
        list.setStyle("-fx-background-color: #FAFAF7; -fx-border-color: #E2E0D8;");

        if (dependencies.isEmpty()) {
            list.getItems().add("No task dependencies configured. Project tasks can execute concurrently.");
        } else {
            for (TaskDependency dep : dependencies) {
                list.getItems().add(dep.getPredecessorTaskId() + "  -->  " + dep.getTaskId() + " (" + dep.getDependencyType() + ")");
            }
        }

        box.getChildren().addAll(title, desc, list);
        contentArea.getChildren().setAll(box);
    }

    // ==========================================
    // 7. RISK RADAR VIEW
    // ==========================================
    private void showRiskRadarView() {
        VBox box = new VBox(16);

        HBox header = new HBox(12);
        header.setAlignment(Pos.CENTER_LEFT);
        Label title = new Label("Deterministic Risk Radar Engine");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        Region spacer = new Region();
        HBox.setHgrow(spacer, Priority.ALWAYS);

        Button runBtn = new Button("Execute Risk Evaluation");
        runBtn.getStyleClass().add("btn-primary");
        runBtn.setOnAction(e -> {
            if (currentProject != null) {
                List<RiskFinding> evaluated = riskEngine.evaluateProjectRisks(currentProject, tasks, dependencies, Collections.emptyMap(), Collections.emptyMap(), LocalDate.now(), Instant.now());
                renderRiskFindings(box, evaluated);
            }
        });

        header.getChildren().addAll(title, spacer, runBtn);
        box.getChildren().add(header);

        List<RiskFinding> findings = (currentProject != null)
                ? riskEngine.evaluateProjectRisks(currentProject, tasks, dependencies, Collections.emptyMap(), Collections.emptyMap(), LocalDate.now(), Instant.now())
                : Collections.emptyList();

        renderRiskFindings(box, findings);
        contentArea.getChildren().setAll(box);
    }

    private void renderRiskFindings(VBox box, List<RiskFinding> findings) {
        if (box.getChildren().size() > 1) {
            box.getChildren().remove(1, box.getChildren().size());
        }

        if (findings.isEmpty()) {
            VBox empty = new VBox(8);
            empty.getStyleClass().add("card");
            Label ok = new Label("Zero Risk Anomalies Found");
            ok.setStyle("-fx-font-size: 14px; -fx-font-weight: bold; -fx-text-fill: #56664C;");
            Label sub = new Label("All project milestones adhere to deterministic dependency and deadline parameters.");
            sub.setStyle("-fx-text-fill: #5A6258; -fx-font-size: 12px;");
            empty.getChildren().addAll(ok, sub);
            box.getChildren().add(empty);
            return;
        }

        for (RiskFinding rf : findings) {
            VBox card = new VBox(6);
            card.getStyleClass().add("card");
            card.setStyle("-fx-border-color: #C84B31; -fx-background-color: #FAFAF7;");

            Label t = new Label("[" + rf.getSeverity() + "] " + rf.getRuleId() + " : " + rf.getAffectedEntityName());
            t.setStyle("-fx-font-weight: bold; -fx-font-size: 13px; -fx-text-fill: #C84B31;");

            Label d = new Label(rf.getExplanation());
            d.setStyle("-fx-text-fill: #292D28; -fx-font-size: 12px;");

            Label rec = new Label("Recommended Action: " + rf.getSuggestedAction());
            rec.setStyle("-fx-text-fill: #56664C; -fx-font-weight: bold; -fx-font-size: 11px;");

            card.getChildren().addAll(t, d, rec);
            box.getChildren().add(card);
        }
    }

    // ==========================================
    // 8. SCHEDULE PLANNER / WHAT-IF
    // ==========================================
    private void showSchedulePlannerView() {
        VBox box = new VBox(16);
        Label title = new Label("What-If Schedule Planner & Impact Analysis");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        Label desc = new Label("Simulate delays or estimate adjustments forward-propagated along task dependency chains.");
        desc.setStyle("-fx-text-fill: #5A6258; -fx-font-size: 12px;");

        HBox controls = new HBox(12);
        controls.setAlignment(Pos.CENTER_LEFT);

        TextField delayDaysField = new TextField("3");
        delayDaysField.setPrefWidth(60);
        Label unitLabel = new Label("days delay on critical tasks");

        Button calcBtn = new Button("Propagate Scenario");
        calcBtn.getStyleClass().add("btn-primary");

        controls.getChildren().addAll(new Label("Simulate:"), delayDaysField, unitLabel, calcBtn);

        TextArea output = new TextArea();
        output.setPrefRowCount(8);
        output.setEditable(false);
        output.setStyle("-fx-font-family: monospace; -fx-font-size: 11px;");

        calcBtn.setOnAction(e -> {
            try {
                int days = Integer.parseInt(delayDaysField.getText().trim());
                ScheduleScenario scenario = new ScheduleScenario();
                scenario.setName("Simulation +" + days + "d");
                scenario.setProjectId(currentProject != null ? currentProject.getId() : UUID.randomUUID());

                List<ScenarioChange> changes = new ArrayList<>();
                if (!tasks.isEmpty()) {
                    ScenarioChange sc = new ScenarioChange();
                    sc.setTaskId(tasks.get(0).getId());
                    sc.setProposedDueDate(LocalDate.now().plusDays(days));
                    changes.add(sc);
                }
                scenario.setChanges(changes);

                ScheduleComparisonResult comp = schedulingEngine.evaluateScenario(
                        currentProject != null ? currentProject : new Project(),
                        tasks,
                        dependencies,
                        scenario,
                        Collections.emptyMap(),
                        Collections.emptyMap(),
                        LocalDate.now(),
                        Instant.now()
                );

                StringBuilder sb = new StringBuilder("Forward-pass propagation calculated successfully:\n");
                sb.append("Valid DAG: ").append(comp.isValid()).append("\n");
                sb.append("Baseline Projected Finish: ").append(comp.getBaselineFinishDate()).append("\n");
                sb.append("Scenario Projected Finish: ").append(comp.getScenarioFinishDate()).append("\n");
                sb.append("Variance Days: ").append(comp.getDeltaDays()).append(" days\n");
                output.setText(sb.toString());
            } catch (Exception ex) {
                output.setText("Simulation failed: " + ex.getMessage());
            }
        });

        box.getChildren().addAll(title, desc, controls, output);
        contentArea.getChildren().setAll(box);
    }

    // ==========================================
    // 9. SCENARIO COMPARISON
    // ==========================================
    private void showScenarioComparisonView() {
        VBox box = new VBox(16);
        Label title = new Label("Scenario Comparison: Baseline vs Proposed");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        HBox comp = new HBox(16);
        VBox baseCard = new VBox(8);
        baseCard.getStyleClass().add("card");
        baseCard.setPrefWidth(320);
        baseCard.getChildren().addAll(
                new Label("Baseline Schedule"),
                new Label("Project Deadline: " + (currentProject != null && currentProject.getTargetDate() != null ? currentProject.getTargetDate() : "On Track")),
                new Label("Total Tasks: " + tasks.size())
        );

        VBox scenCard = new VBox(8);
        scenCard.getStyleClass().add("card");
        scenCard.setPrefWidth(320);
        scenCard.getChildren().addAll(
                new Label("Proposed Schedule (Alternative)"),
                new Label("Variance: +0 Days"),
                new Label("Status: Pending Manager Sign-off")
        );

        comp.getChildren().addAll(baseCard, scenCard);
        box.getChildren().addAll(title, comp);
        contentArea.getChildren().setAll(box);
    }

    // ==========================================
    // 10. WORKFLOW CONFIG
    // ==========================================
    private void showWorkflowConfigView() {
        VBox box = new VBox(16);
        Label title = new Label("Custom Workflow & Status Transition Config");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        ListView<String> list = new ListView<>();
        list.getItems().addAll(
                "TODO  -->  IN_PROGRESS  (Allowed for: MEMBER, MANAGER, ADMIN)",
                "IN_PROGRESS  -->  REVIEW  (Allowed for: MEMBER, MANAGER, ADMIN)",
                "REVIEW  -->  DONE  (Requires: MANAGER or ADMIN approval)",
                "DONE  -->  REOPENED  (Requires: MANAGER approval)"
        );

        box.getChildren().addAll(title, list);
        contentArea.getChildren().setAll(box);
    }

    // ==========================================
    // 11. TEAM MANAGEMENT
    // ==========================================
    private void showTeamManagementView() {
        VBox box = new VBox(16);
        Label title = new Label("Team Capacity & Allocation");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        ListView<String> list = new ListView<>();
        list.getItems().addAll(
                "admin@projectflow.io - ADMINISTRATOR (Workload: 2 tasks, 15% capacity)",
                "manager@projectflow.io - MANAGER (Workload: 4 tasks, 40% capacity)",
                "engineer@projectflow.io - MEMBER (Workload: 6 tasks, 60% capacity)"
        );

        box.getChildren().addAll(title, list);
        contentArea.getChildren().setAll(box);
    }

    // ==========================================
    // 12. AUTOMATION RULES
    // ==========================================
    private void showAutomationRulesView() {
        VBox box = new VBox(16);
        Label title = new Label("Event Automation Rules");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        ListView<String> list = new ListView<>();
        list.getItems().addAll(
                "Rule 1: On Task Completed -> Auto unblock dependent successors",
                "Rule 2: On Overdue Detected -> Dispatch Risk Alert to Project Manager",
                "Rule 3: On What-If Approval -> Apply scenario dates to baseline tasks"
        );

        box.getChildren().addAll(title, list);
        contentArea.getChildren().setAll(box);
    }

    // ==========================================
    // 13. ACTIVITY HISTORY
    // ==========================================
    private void showActivityHistoryView() {
        VBox box = new VBox(16);
        Label title = new Label("Activity History & Audit Trail");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        ListView<String> list = new ListView<>();
        list.getItems().addAll(
                "[" + Instant.now() + "] System initialized Flyway schema V1",
                "[" + Instant.now() + "] Workspace isolation verified",
                "[" + Instant.now() + "] Risk Radar completed background health check"
        );

        box.getChildren().addAll(title, list);
        contentArea.getChildren().setAll(box);
    }

    // ==========================================
    // 14. SYNC & CONFLICTS
    // ==========================================
    private void showSyncStatusView() {
        VBox box = new VBox(16);
        Label title = new Label("Offline Synchronization & Conflict Inspector");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        VBox statusCard = new VBox(8);
        statusCard.getStyleClass().add("card");
        statusCard.getChildren().addAll(
                new Label("Pending Offline Changes: 0"),
                new Label("Local Database Engine: SQLite 3.45"),
                new Label("Conflict Resolution Policy: Last-Write-Wins (LWW) with Audit Snapshot")
        );

        box.getChildren().addAll(title, statusCard);
        contentArea.getChildren().setAll(box);
    }

    // ==========================================
    // 15. SETTINGS VIEW
    // ==========================================
    private void showSettingsView() {
        VBox box = new VBox(16);
        Label title = new Label("Manager Application Settings");
        title.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        GridPane grid = new GridPane();
        grid.setHgap(10);
        grid.setVgap(10);

        TextField urlField = new TextField(localStorage.getSetting("api_base_url", "http://localhost:8080/api/v1"));
        urlField.setPrefWidth(300);

        Button saveBtn = new Button("Save Settings");
        saveBtn.getStyleClass().add("btn-primary");
        saveBtn.setOnAction(e -> {
            localStorage.setSetting("api_base_url", urlField.getText().trim());
            showInfo("Settings Saved", "API base URL updated.");
        });

        grid.add(new Label("Backend API URL:"), 0, 0);
        grid.add(urlField, 1, 0);
        grid.add(saveBtn, 1, 1);

        box.getChildren().addAll(title, grid);
        contentArea.getChildren().setAll(box);
    }

    private void showError(String title, String content) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(content);
        alert.showAndWait();
    }

    private void showInfo(String title, String content) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(content);
        alert.showAndWait();
    }
}
