Sub SetNumberOfSeries(chart As Object, n As Integer)

    If chart.SeriesCollection.Count < n Then
        While chart.SeriesCollection.Count < n
            chart.SeriesCollection.NewSeries
        Wend
    ElseIf chart.SeriesCollection.Count > n Then
        While chart.SeriesCollection.Count > n
            chart.SeriesCollection(chart.SeriesCollection.Count).Delete
        Wend
    End If

End Sub

Sub DrawCategoryGraph(titleStr As String, xLabelStr As String, yLabelStr As String, seriesCount As Integer, recCount As Integer)

    Dim currShape As Object: Set currShape = ActiveSheet.Shapes.AddChart2(239, xlLineMarkers)
    Dim currChart As Object: Set currChart = currShape.chart

    currChart.HasTitle = True
    currChart.ChartTitle.Text = titleStr
    currChart.ChartTitle.Select
    Selection.Format.TextFrame2.TextRange.Font.Size = 18

    SetNumberOfSeries currChart, seriesCount

    currChart.SetElement (msoElementPrimaryValueGridLinesMajor)
    currChart.SetElement (msoElementPrimaryCategoryGridLinesNone)

    currShape.ScaleWidth 1.75, msoFalse, msoScaleFromBottomRight
    currShape.ScaleHeight 1.75, msoFalse, msoScaleFromBottomRight

    Dim i As Integer

    For i = 1 To seriesCount
        currChart.FullSeriesCollection(i).Name = "=" & ActiveSheet.Name & "!" & ActiveSheet.Cells(1, 1 + i).Address()
        currChart.FullSeriesCollection(i).XValues = Range(Cells(1 + 1, 1), Cells(1 + recCount, 1))
        currChart.FullSeriesCollection(i).Values = Range(Cells(1 + 1, 1 + i), Cells(1 + recCount, 1 + i))
        currChart.FullSeriesCollection(i).HasErrorBars = True

        maxYErrRange = Range(Cells(1 + 1, 1 + (2 * seriesCount) + i), Cells(1 + recCount, 1 + (2 * seriesCount) + i))
        minYErrRange = Range(Cells(1 + 1, 1 + (1 * seriesCount) + i), Cells(1 + recCount, 1 + (1 * seriesCount) + i))

        currChart.FullSeriesCollection(i).ErrorBar _
                                          Direction:=xlY, _
                                          Include:=xlErrorBarIncludeBoth, _
                                          Type:=xlErrorBarTypeCustom, _
                                          Amount:=maxYErrRange, _
                                          MinusValues:=minYErrRange
    Next i

    currChart.SetElement (msoElementPrimaryCategoryAxisTitleAdjacentToAxis)
    currChart.Axes(xlCategory).HasTitle = True
    currChart.Axes(xlCategory).AxisTitle.Text = xLabelStr
    currChart.Axes(xlCategory).AxisTitle.Select
    Selection.Format.TextFrame2.TextRange.Font.Size = 12

    currChart.SetElement (msoElementPrimaryValueAxisTitleAdjacentToAxis)
    currChart.Axes(xlValue).HasTitle = True
    currChart.Axes(xlValue).AxisTitle.Text = yLabelStr
    currChart.Axes(xlValue).AxisTitle.Select
    Selection.Format.TextFrame2.TextRange.Font.Size = 12

End Sub

Sub DrawXyGraph(titleStr As String, xLabelStr As String, yLabelStr As String, seriesCount As Integer, recCount As Integer)

    Dim currShape As Object: Set currShape = ActiveSheet.Shapes.AddChart2(240, xlXYScatterLines)
    Dim currChart As Object: Set currChart = currShape.chart

    currChart.HasTitle = True
    currChart.ChartTitle.Text = titleStr
    currChart.ChartTitle.Select
    Selection.Format.TextFrame2.TextRange.Font.Size = 18

    SetNumberOfSeries currChart, seriesCount
    
    currShape.ScaleWidth 1.75, msoFalse, msoScaleFromBottomRight
    currShape.ScaleHeight 1.75, msoFalse, msoScaleFromBottomRight

    
    For i = 1 To seriesCount
        currChart.FullSeriesCollection(i).Name = "=" & ActiveSheet.Name & "!" & ActiveSheet.Cells(1, 1 + (i * 2)).Address()
        currChart.FullSeriesCollection(i).XValues = Range(Cells(1 + 1, 1 + (i * 2) - 1), Cells(1 + recCount, 1 + (i * 2) - 1))
        currChart.FullSeriesCollection(i).Values = Range(Cells(1 + 1, 1 + (i * 2)), Cells(1 + recCount, 1 + (i * 2)))

        Dim maxYErrRange As Object: Set maxYErrRange = Range(Cells(1 + 1, 1 + (2 * 2 * seriesCount) + (i * 2)), Cells(1 + recCount, 1 + (2 * 2 * seriesCount) + (i * 2)))
        Dim minYErrRange As Object: Set minYErrRange = Range(Cells(1 + 1, 1 + (1 * 2 * seriesCount) + (i * 2)), Cells(1 + recCount, 1 + (1 * 2 * seriesCount) + (i * 2)))

        currChart.FullSeriesCollection(i).HasErrorBars = True
        currChart.FullSeriesCollection(i).ErrorBar _
                                          Direction:=xlY, _
                                          Include:=xlErrorBarIncludeBoth, _
                                          Type:=xlErrorBarTypeCustom, _
                                          Amount:=maxYErrRange, _
                                          MinusValues:=minYErrRange
    Next i

    currChart.SetElement (msoElementPrimaryCategoryAxisTitleAdjacentToAxis)
    currChart.Axes(xlCategory).HasTitle = True
    currChart.Axes(xlCategory).AxisTitle.Text = xLabelStr
    currChart.Axes(xlCategory).AxisTitle.Select
    Selection.Format.TextFrame2.TextRange.Font.Size = 12

    currChart.SetElement (msoElementPrimaryValueAxisTitleAdjacentToAxis)
    currChart.Axes(xlValue).HasTitle = True
    currChart.Axes(xlValue).AxisTitle.Text = yLabelStr
    currChart.Axes(xlValue).AxisTitle.Select
    Selection.Format.TextFrame2.TextRange.Font.Size = 12

End Sub

Sub DrawGraph()
'
' DrawGraph Macro
'
' Shortcut: Ctrl+Shift+D
'

    ActiveSheet.Cells(1, 1).Select

    Dim titleStr As String: titleStr = "Title Not Found"
    Dim xLabelStr As String: xLabelStr = "xLabel Not Found"
    Dim yLabelStr As String: yLabelStr = "yLabel Not Found"
    Dim graphType As String: graphType = "Graph Type Not Fount"
    Dim seriesCount As Integer: seriesCount = 0
    Dim recCount As Integer: recCount = 0

    Dim isInfoFound As Boolean: isInfoFound = False

    Set indexSheet = Worksheets("Index")

    Dim i As Long: i = 1
    While ((Not IsEmpty(indexSheet.Cells(i, 1).Value)) And (Not isInfoFound))
        If indexSheet.Cells(i, 1).Value = ActiveSheet.Name Then
            titleStr = indexSheet.Cells(i, 2).Value
            xLabelStr = indexSheet.Cells(i, 3).Value
            yLabelStr = indexSheet.Cells(i, 4).Value
            seriesCount = CInt(indexSheet.Cells(i, 5).Value)
            recCount = CInt(indexSheet.Cells(i, 6).Value)
            graphType = indexSheet.Cells(i, 7).Value

            isInfoFound = True
        End If
        
        i = i + 1
    Wend

    If Not isInfoFound Then
        MsgBox Prompt:="Cannot find the information for the graph, " & ActiveSheet.Name & ", in Index sheet!", Title:="Error"
        Exit Sub
    End If

    'infoStr = "titleStr   " & vbTab & vbTab & CStr(VarType(titleStr)) & vbTab & ": " & titleStr & vbCrLf & _
    '          "xLabelStr  " & vbTab & CStr(VarType(xLabelStr)) & vbTab & ": " & xLabelStr & vbCrLf & _
    '          "yLabelStr  " & vbTab & CStr(VarType(yLabelStr)) & vbTab & ": " & yLabelStr & vbCrLf & _
    '          "seriesCount" & vbTab & CStr(VarType(seriesCount)) & vbTab & ": " & CStr(seriesCount) & vbCrLf & _
    '          "recCount   " & vbTab & CStr(VarType(recCount)) & vbTab & ": " & CStr(recCount) & vbCrLf & _
    '          "graphType  " & vbTab & CStr(VarType(graphType)) & vbTab & ": " & graphType

    'MsgBox Prompt:=infoStr, Title:="Debug Info"

    If graphType = "CATEGORY" Then
        DrawCategoryGraph titleStr, xLabelStr, yLabelStr, seriesCount, recCount
    ElseIf graphType = "XY" Then
        DrawXyGraph titleStr, xLabelStr, yLabelStr, seriesCount, recCount
    Else
        MsgBox Prompt:="Unrecognized graph type, " & graphType & "!", Title:="Error"
    End If

    ActiveSheet.Cells(1, 1).Select

End Sub
